-- query para conferir se a soma final dos valores está igual a soma final dos preços do dataset inteiro de pedidos

WITH cte_orders AS (
	SELECT 
		oi.order_id,
		o.customer_id,
		o.order_status,
		o.order_purchase_timestamp,
		SUM(oi.price) AS total_price
	FROM order_items AS oi

	INNER JOIN orders AS o
		ON o.order_id = oi.order_id
		
	WHERE o.order_status = 'delivered'

	GROUP BY 
		oi.order_id,
		o.order_status
),

max_date AS (
	SELECT
		MAX(order_purchase_timestamp) AS max_purchase_date
	FROM orders
),

date_diff AS (
	SELECT 
		orders.customer_id,
		orders.order_id,
		orders.order_purchase_timestamp,
		ROUND(julianday(max_date.max_purchase_date) - julianday(orders.order_purchase_timestamp), 0) AS date_difference
	FROM orders
	
	JOIN max_date
	
	WHERE order_status = 'delivered'
),

final_rfm AS (
	SELECT
		c.customer_unique_id,
		--d.date_difference,
		--cte_orders.order_id,
		--cte_orders.total_price
		CAST(MIN(d.date_difference) AS INTEGER) AS days_last_purchase,
		COUNT(cte_orders.order_id) AS total_purchases,
		ROUND(SUM(cte_orders.total_price), 2) AS total_price_per_client
	FROM cte_orders

	INNER JOIN customers AS c
		ON c.customer_id = cte_orders.customer_id

	INNER JOIN date_diff AS d
		ON d.customer_id = cte_orders.customer_id
		AND d.order_id = cte_orders.order_id

	--WHERE customer_unique_id = '8d50f5eadf50201ccdcedfb9e2ac8455'	
	GROUP BY c.customer_unique_id
)

SELECT SUM(total_price_per_client) AS soma_rfm
FROM final_rfm