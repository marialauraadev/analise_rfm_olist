-- query para obter a soma final dos preços dos pedidos

SELECT
	SUM(price) AS total_price_dataset
FROM order_items

INNER JOIN orders	
	ON orders.order_id = order_items.order_id

WHERE orders.order_status = 'delivered';