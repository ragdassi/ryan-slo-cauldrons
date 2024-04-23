--Barrels
UPDATE global_inventory SET gold = gold - :gold, green_ml = green_ml + :green_ml
UPDATE global_inventory SET gold = gold - :gold, red_ml = red_ml + :red_ml
UPDATE global_inventory SET gold = gold - :gold, blue_ml = blue_ml + :blue_ml
UPDATE global_inventory SET gold = gold - :gold, dark_ml = dark_ml + :dark_ml
SELECT gold FROM global_inventory

--Bottlers
SELECT * FROM potions WHERE red = :red AND green = :green AND blue = :blue AND dark = :dark
UPDATE global_inventory SET red_ml = red_ml - :red_ml
UPDATE global_inventory SET green_ml = green_ml - :green_ml
UPDATE global_inventory SET blue_ml = blue_ml - :blue_ml
UPDATE global_inventory SET dark_ml = dark_ml - :dark_ml
UPDATE potions SET quantity = quantity + :quantity WHERE sku = :sku
SELECT red_ml from global_inventory
SELECT green_ml from global_inventory
SELECT blue_ml from global_inventory
SELECT dark_ml from global_inventory
SELECT * from potions

--Carts
SELECT customer_id from carts
INSERT INTO carts (customer_id) VALUES (:customer_id)
UPDATE cart_items SET item_quantity = :item_quantity WHERE item_sku = :item_sku
SELECT * from cart_items
UPDATE global_inventory SET num_potions = num_potions - :num_potions
UPDATE global_inventory SET gold = gold + :gold

--Catalog
SELECT quantity, sku, red, green, blue, dark, price from potions

--Admin
UPDATE global_inventory SET gold = :gold
UPDATE potions SET quantity = 0
UPDATE global_inventory SET green_ml = :green_ml, red_ml = :red_ml, blue_ml = :blue_ml, dark_ml = :dark_ml

--Inventory
SELECT green_ml FROM global_inventor
SELECT red_ml FROM global_inventory
SELECT blue_ml FROM global_inventory
SELECT dark_ml FROM global_inventor
SELECT gold FROM global_inventory
SELECT SUM(quantity) AS total_quantity FROM potions