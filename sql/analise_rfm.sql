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
)

SELECT
	c.customer_unique_id,
	COUNT(cte_orders.order_id) AS total_purchases,
	MAX(order_purchase_timestamp) AS last_purchase,
	SUM(total_price) AS total_price_per_client
FROM cte_orders

INNER JOIN customers AS c
	ON c.customer_id = cte_orders.customer_id

GROUP BY c.customer_unique_id