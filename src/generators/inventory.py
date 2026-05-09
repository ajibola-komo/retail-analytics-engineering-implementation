import numpy as np
from src.config.paths import (INVENTORY_DDL_PATH, INVENTORY_PARQUET_PATH)
from src.config.constants import (SHRINKAGE_RATE_Y1, SHRINKAGE_RATE_Y2, SHRINKAGE_RATE_Y3, Y1, Y2, Y3, INVENTORY_START_ID)


def generate_inventories(conn):

    create_db = INVENTORY_DDL_PATH.read_text()
    conn.execute(create_db)

    query = '''
        WITH MONTH_SPINE AS (
            SELECT DISTINCT date_trunc('month', transaction_timestamp) AS month_start
            FROM fact_transaction
        ),
        SKU_GRID AS (
            SELECT p.product_id, s.store_id, m.month_start AS snapshot_month
            FROM dim_product AS p
            CROSS JOIN dim_store AS s
            CROSS JOIN MONTH_SPINE AS m
        ),
        MONTHLY_SALES AS (
            SELECT
                s.product_id,
                t.store_id,
                date_trunc('month', t.transaction_timestamp) AS snapshot_month,
                SUM(s.quantity) AS sold_units
            FROM fact_transaction AS t
            INNER JOIN fact_sale AS s ON t.transaction_id = s.transaction_id
            WHERE t.transaction_status = 'Completed'
            GROUP BY s.product_id, t.store_id, snapshot_month
        )
        SELECT
            g.product_id,
            g.store_id,
            g.snapshot_month,
            COALESCE(s.sold_units, 0) AS sold_units
        FROM sku_grid AS g
        LEFT JOIN monthly_sales s
            ON s.product_id = g.product_id
            AND s.store_id = g.store_id
            AND s.snapshot_month = g.snapshot_month
        ORDER BY g.product_id, g.store_id, g.snapshot_month
    '''

    sku_grid = conn.execute(query).df()

    stock_skeleton = sku_grid[['product_id', 'store_id', 'snapshot_month']].copy()
    stock_skeleton['sold_units']     = sku_grid['sold_units']
    stock_skeleton['starting_stock'] = 0
    stock_skeleton['received_stock'] = 0
    stock_skeleton['closing_stock']  = 0
    stock_skeleton['backorder_flag'] = False
    stock_skeleton['shrinkage_loss'] = 0
    

    # ── 4. First-month starting stock ────────────────────────────────────────
    first_month = stock_skeleton['snapshot_month'].min()
    mask = stock_skeleton['snapshot_month'] == first_month
    first_month_sales = stock_skeleton.loc[mask, 'sold_units']

    stock_skeleton.loc[mask, 'starting_stock'] = np.maximum(
        np.random.randint(25, 50, size=mask.sum()),
        (first_month_sales * 1.5).astype(int)
    )

    # ── 5. Replenishment with intentional stockout variance ───────────────────
    #   ~20 % of records are deliberately under-replenished so that closing
    #   stock can hit zero and produce realistic stockout / backorder events.
    n = len(stock_skeleton)
    replenishment_factor = np.where(
        np.random.rand(n) < 0.20,
        np.random.uniform(0.5, 0.9, n),   # under-stocked → potential stockout
        np.random.uniform(1.1, 1.5, n)    # over-stocked  → healthy buffer
    )

    stock_skeleton['received_stock'] = np.maximum(
        np.random.randint(0, 10, size=n),
        (stock_skeleton['sold_units'] * replenishment_factor).astype(int)
    )

    # ── 6. Shrinkage ──────────────────────────────────────────────────────────
    #   Use randint(1, 5) so records flagged as shrinkage events actually carry
    #   a meaningful unit loss (original code used 0–1 which was almost always 0).

    stock_skeleton = stock_skeleton.sort_values(
    by=['product_id', 'store_id', 'snapshot_month']
).reset_index(drop=True)
    
    stock_skeleton['inventory_id']   = np.arange(INVENTORY_START_ID, INVENTORY_START_ID + len(stock_skeleton))

    stock_skeleton['year'] = stock_skeleton['snapshot_month'].dt.year
    
    isyear1 = np.where(stock_skeleton['year'] == Y1)[0]
    isyear2 = np.where(stock_skeleton['year'] == Y2)[0]
    isyear3 = np.where(stock_skeleton['year'] == Y3)[0]

    has_shrinkage = np.zeros(n, dtype=bool)
    has_shrinkage[isyear1] = np.random.rand(len(isyear1)) <= SHRINKAGE_RATE_Y1
    has_shrinkage[isyear2] = np.random.rand(len(isyear2)) <= SHRINKAGE_RATE_Y2
    has_shrinkage[isyear3] = np.random.rand(len(isyear3)) <= SHRINKAGE_RATE_Y3

    stock_skeleton.loc[has_shrinkage, 'shrinkage_loss'] = np.random.randint(
        1, 5, size=has_shrinkage.sum()
    )

    # ── 7. Compute closing stock via cumulative window (DuckDB) ───────────────
    conn.register("stock_data", stock_skeleton)

    query = '''
        WITH inventory_flow AS (
            SELECT
                inventory_id,
                product_id,
                store_id,
                snapshot_month,
                received_stock,
                sold_units,
                shrinkage_loss,

                SUM(received_stock - sold_units - shrinkage_loss)
                    OVER (
                        PARTITION BY product_id, store_id
                        ORDER BY snapshot_month
                    ) AS cumulative_net,

                FIRST_VALUE(starting_stock)
                    OVER (
                        PARTITION BY product_id, store_id
                        ORDER BY snapshot_month
                    ) AS initial_stock

            FROM stock_data
        ),

        final_inventory AS (
            SELECT
                inventory_id,
                product_id,
                store_id,
                snapshot_month,
                initial_stock,

                -- raw value used to detect backorders (can go negative)
                initial_stock + cumulative_net AS raw_closing_stock,

                -- floor at 0 — cannot hold negative physical stock
                GREATEST(initial_stock + cumulative_net, 0)    AS closing_stock,

                received_stock,
                sold_units,
                shrinkage_loss
            FROM inventory_flow
        )

        INSERT INTO INVENTORY
        SELECT
            inventory_id,
            product_id,
            store_id,
            snapshot_month,

            -- starting_stock = previous month closing_stock
            LAG(closing_stock, 1, initial_stock)
                OVER (PARTITION BY product_id, store_id ORDER BY snapshot_month),

            received_stock,
            sold_units,
            closing_stock,

            -- backorder occurs when raw value goes negative
            raw_closing_stock < 0   AS backorder_flag,

            shrinkage_loss
        FROM final_inventory
    '''

    conn.execute(query)

    # ── 8. Export ─────────────────────────────────────────────────────────────
    conn.execute(f"COPY INVENTORY TO '{INVENTORY_PARQUET_PATH}' (FORMAT PARQUET)")