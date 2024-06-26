--cart items
create table
  public.cart_items (
    item_id bigint generated by default as identity,
    item_sku text null,
    cart_id bigint null,
    item_quantity bigint null,
    item_price bigint null,
    constraint cart_items_pkey primary key (item_id),
    constraint public_cart_items_cart_id_fkey foreign key (cart_id) references carts (id)
  ) tablespace pg_default;

--carts
  create table
  public.carts (
    id bigint generated by default as identity,
    customer_id text null,
    constraint carts_pkey primary key (id)
  ) tablespace pg_default;

--global inventory
  create table
  public.global_inventory (
    num_green_potions integer generated by default as identity,
    num_green_ml integer not null,
    gold integer null,
    green_ml integer null default 0,
    red_ml integer null default 0,
    blue_ml integer null default 0,
    num_blue_potions integer null default 0,
    num_red_potions integer null default 0,
    num_potions integer null,
    id bigint generated by default as identity,
    dark_ml bigint null default '0'::bigint,
    constraint global_inventory_pkey primary key (id)
  ) tablespace pg_default;

--potions
  create table
  public.potions (
    id bigint generated by default as identity,
    sku text not null,
    red bigint null,
    green bigint null,
    blue bigint null,
    dark bigint null,
    quantity bigint null,
    price bigint null,
    constraint potions_pkey primary key (id)
  ) tablespace pg_default;