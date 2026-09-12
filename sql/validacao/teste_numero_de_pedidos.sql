SELECT
	customer_unique_id,
	COUNT(orders.order_id) AS number_of_orders
FROM customers

INNER JOIN orders
	ON orders.customer_id = customers.customer_id
	
WHERE orders.order_status = 'delivered'	
GROUP BY customer_unique_id
HAVING COUNT (*) > 1

ORDER BY number_of_orders DESC


