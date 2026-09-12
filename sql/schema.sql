CREATE TABLE IF NOT EXISTS "customers" (
	"customer_id"	TEXT,
	"customer_unique_id"	TEXT,
	"customer_zip_code_prefix"	TEXT,
	"customer_city"	TEXT,
	"customer_state"	TEXT,
	PRIMARY KEY("customer_id")
);
CREATE TABLE IF NOT EXISTS "order_items" (
	"order_id"	TEXT,
	"order_item_id"	INTEGER,
	"product_id"	TEXT,
	"seller_id"	TEXT,
	"shipping_limit_date"	TEXT,
	"price"	REAL,
	"freight_value"	REAL,
	PRIMARY KEY("order_id","order_item_id"),
	FOREIGN KEY("order_id") REFERENCES "orders"("order_id"),
	FOREIGN KEY("product_id") REFERENCES "products"("product_id")
);
CREATE TABLE IF NOT EXISTS "orders" (
	"order_id"	TEXT,
	"customer_id"	TEXT,
	"order_status"	TEXT,
	"order_purchase_timestamp"	TEXT,
	"order_approved_at"	TEXT,
	"order_delivered_carrier_date"	TEXT,
	"order_delivered_customer_date"	TEXT,
	"order_estimated_delivery_date"	TEXT,
	PRIMARY KEY("order_id"),
	FOREIGN KEY("customer_id") REFERENCES "customers"("customer_id")
);
CREATE TABLE IF NOT EXISTS "products" (
	"product_id"	TEXT,
	"product_category_name"	TEXT,
	"product_name_lenght"	INTEGER,
	"product_description_lenght"	INTEGER,
	"product_photos_qty"	INTEGER,
	"product_weight_g"	INTEGER,
	"product_length_cm"	INTEGER,
	"product_height_cm"	INTEGER,
	"product_width_cm"	INTEGER,
	PRIMARY KEY("product_id")
);