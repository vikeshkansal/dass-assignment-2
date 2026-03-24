# QuickCart API — Test Report

**Role Number:** 2024101126
**Test suite:** `tests/test_quickcart.py` (109 tests)
**Results:** 90 passed · 19 failed
**Bugs confirmed:** 15 server-side bugs across 13 distinct root causes

---

## Part 1 — Test Cases

> **Common headers:** Every request includes `X-Roll-Number: 2024101126`. User-scoped endpoints also include `X-User-ID: {user_id}` and `Content-Type: application/json` where a body is sent. These are omitted from individual entries below for brevity.

---

### Section 1 — Header Validation

**1. test_missing_roll_number_returns_401**
- Input: `GET /admin/users` — no headers
- Expected: `401`
- Why: Confirms the server enforces the mandatory roll number header on every request.

**2. test_invalid_roll_number_returns_400**
- Input: `GET /admin/users` with `X-Roll-Number: abc`
- Expected: `400`
- Why: A non-integer roll number is structurally invalid and must be rejected before processing.

**3. test_missing_user_id_on_user_endpoint_returns_400**
- Input: `GET /profile` with only `X-Roll-Number` (no `X-User-ID`)
- Expected: `400`
- Why: User-scoped endpoints require a user ID; missing it must be caught at the gate.

**4. test_invalid_user_id_returns_400**
- Input: `GET /profile` with `X-User-ID: abc`
- Expected: `400`
- Why: A non-integer user ID is invalid and must be rejected rather than silently ignored.

**5. test_negative_user_id_returns_400**
- Input: `GET /profile` with `X-User-ID: -1`
- Expected: `400`
- Why: User IDs must be positive integers; negative values should be rejected.

**6. test_zero_user_id_returns_400**
- Input: `GET /profile` with `X-User-ID: 0`
- Expected: `400`
- Why: Zero is not a valid user ID and must be treated as a bad request.

**7. test_nonexistent_user_returns_error**
- Input: `GET /profile` with `X-User-ID: 99999`
- Expected: `400` or `404`
- Why: A user ID that exists in neither the DB nor any valid range must produce an error, not a 200.

**8. test_admin_endpoint_does_not_require_user_id**
- Input: `GET /admin/users` with only `X-Roll-Number`
- Expected: `200`
- Why: Admin endpoints explicitly do not require `X-User-ID`; this confirms they are not over-restricted.

---

### Section 2 — Admin Endpoints

**9. test_admin_users**
- Input: `GET /admin/users`
- Expected: `200`, non-empty list, each item has `user_id`, `name`, `wallet_balance`, `loyalty_points`
- Why: Validates that the admin users endpoint returns complete user records for use as ground truth.

**10. test_admin_users_specific**
- Input: `GET /admin/users/1`
- Expected: `200`, `user_id == 1`
- Why: Confirms single-user lookup works and returns the correct user.

**11. test_admin_users_nonexistent**
- Input: `GET /admin/users/99999`
- Expected: `404`
- Why: Looking up a user that does not exist must return 404, not a 200 with empty data.

**12. test_admin_products**
- Input: `GET /admin/products`
- Expected: `200`, list includes at least some inactive products
- Why: Admin must return the full unfiltered product list, including inactive ones hidden from users.

**13. test_admin_carts**
- Input: `GET /admin/carts`
- Expected: `200`, list
- Why: Verifies the admin cart endpoint is accessible and returns all carts.

**14. test_admin_orders**
- Input: `GET /admin/orders`
- Expected: `200`, list
- Why: Verifies admin order visibility across all users.

**15. test_admin_coupons**
- Input: `GET /admin/coupons`
- Expected: `200`, list, each coupon has `coupon_code` and `discount_type`
- Why: Confirms coupon data is fully accessible from admin for test setup and verification.

**16. test_admin_tickets**
- Input: `GET /admin/tickets`
- Expected: `200`, list
- Why: Verifies admin can see all support tickets across all users.

**17. test_admin_addresses**
- Input: `GET /admin/addresses`
- Expected: `200`, list
- Why: Verifies the admin address endpoint is accessible and returns all records.

**18. test_profile_update_reflected_in_admin**
- Input: `PUT /profile` body `{"name": "AdminSyncVerify", "phone": "9000000001"}` for user 20, then `GET /admin/users/20`
- Expected: Admin response shows updated `name` and `phone`
- Why: Confirms that writes to user-facing endpoints propagate correctly to the admin view.

**19. test_address_update_reflected_in_admin**
- Input: `POST /addresses` to create, then `PUT /addresses/{id}` to update street, then `GET /admin/addresses`
- Expected: Admin endpoint shows the new street value
- Why: Ensures the admin endpoint reflects the latest data and isn't serving a stale cache.

**20. test_user_cart_matches_admin_cart**
- Input: Add two products to user 22's cart, then compare `GET /cart` (user) vs `GET /admin/carts` (admin)
- Expected: Product IDs and quantities are identical in both views
- Why: Validates that user and admin views of the cart are consistent with each other.

---

### Section 3 — Profile

**21. test_get_profile**
- Input: `GET /profile` for user 1
- Expected: `200`, response has `user_id`, `name`, `email`, `phone`
- Why: Basic smoke test confirming the profile endpoint returns the expected fields.

**22. test_update_profile_valid**
- Input: `PUT /profile` body `{"name": "Updated Name", "phone": "9876543210"}`
- Expected: `200`
- Why: Confirms the happy path for a valid profile update works correctly.

**23. test_update_profile_name_length_boundaries**
- Input: `PUT /profile` with `name: "A"` (1 char), then `name: "A"*51` (51 chars)
- Expected: Both `400`
- Why: Tests both sides of the invalid boundary to confirm the 2–50 character rule is enforced.

**24. test_update_profile_name_boundary_2_chars**
- Input: `PUT /profile` with `name: "AB"` (exactly 2 chars)
- Expected: `200`
- Why: Confirms the minimum valid boundary is accepted, not off-by-one rejected.

**25. test_update_profile_name_boundary_50_chars**
- Input: `PUT /profile` with `name: "A"*50` (exactly 50 chars)
- Expected: `200`
- Why: Confirms the maximum valid boundary is accepted.

**26. test_update_profile_phone_length_boundaries**
- Input: `PUT /profile` with `phone: "123"` (3 digits), then `phone: "12345678901"` (11 digits)
- Expected: Both `400`
- Why: Phone must be exactly 10 digits; anything shorter or longer must be rejected.

---

### Section 4 — Addresses

**27. test_get_addresses**
- Input: `GET /addresses` for user 1
- Expected: `200`, list
- Why: Basic smoke test for the addresses list endpoint.

**28. test_create_address_valid**
- Input: `POST /addresses` body `{"label": "HOME", "street": "123 Main Street", "city": "Mumbai", "pincode": "400001", "is_default": true}`
- Expected: `200`/`201`, response contains `address` object with all fields including `address_id`
- Why: Validates the full happy-path creation response, including that the server returns the new address with its assigned ID.

**29. test_create_address_invalid_label**
- Input: `POST /addresses` body with `"label": "WORK"`
- Expected: `400`
- Why: Only HOME, OFFICE, and OTHER are valid labels; any other value must be rejected.

**30. test_create_address_street_length_boundaries**
- Input: `POST /addresses` with `street: "ab"` (2 chars), then `street: "A"*101` (101 chars)
- Expected: Both `400`
- Why: Street must be 5–100 characters; tests both sides of the invalid range.

**31. test_create_address_city_too_short**
- Input: `POST /addresses` with `city: "A"` (1 char)
- Expected: `400`
- Why: City minimum is 2 characters; a 1-character city must be rejected.

**32. test_create_address_pincode_wrong_length**
- Input: `POST /addresses` with `pincode: "4000"` (4 digits)
- Expected: `400`
- Why: Pincode must be exactly 6 digits; wrong length must be caught.

**33. test_create_default_address_replaces_old_default**
- Input: Create two addresses both with `is_default: true` for user 798, then `GET /addresses`
- Expected: Exactly one address has `is_default: true`
- Why: The spec requires only one default at a time; adding a new default must unset the previous one.

**34. test_update_address_street**
- Input: Create an address, then `PUT /addresses/{id}` body `{"street": "Updated Street Here"}`
- Expected: `200`, response body shows new street value
- Why: Confirms the update response reflects the new data, not the old data *(this test catches Bug 1)*.

**35. test_delete_nonexistent_address_returns_404**
- Input: `DELETE /addresses/99999`
- Expected: `404`
- Why: Deleting a non-existent resource must return 404, not silently succeed.

---

### Section 5 — Products

**36. test_get_products_list**
- Input: `GET /products`
- Expected: `200`, non-empty list
- Why: Basic smoke test confirming the product listing endpoint works.

**37. test_products_list_excludes_inactive**
- Input: `GET /products`
- Expected: Every item in the list has `is_active: true`
- Why: Inactive products must never be shown to users; this enforces the filtering rule.

**38. test_get_product_by_id**
- Input: `GET /products/1`
- Expected: `200`, `product_id == 1`, has `name` and `price`
- Why: Confirms single-product lookup returns the correct record with expected fields.

**39. test_get_nonexistent_product_returns_404**
- Input: `GET /products/99999`
- Expected: `404`
- Why: Looking up a product that does not exist must return 404.

**40. test_filter_by_category**
- Input: `GET /products?category=Fruits`
- Expected: `200`, every returned product has `category == "Fruits"`
- Why: Confirms category filtering works correctly and does not leak products from other categories.

**41. test_search_by_name**
- Input: `GET /products?search=Apple`
- Expected: Non-empty list, every product name contains "apple" (case-insensitive)
- Why: Confirms the name search is functional and returns only relevant results.

**42. test_sort_by_price_ascending**
- Input: `GET /products?sort=price_asc`
- Expected: Prices are in non-decreasing order
- Why: Verifies ascending sort works correctly across the full product list.

**43. test_sort_by_price_descending**
- Input: `GET /products?sort=price_desc`
- Expected: Prices are in non-increasing order
- Why: Verifies descending sort works correctly.

**44. test_product_price_matches_database**
- Input: `GET /admin/products` and `GET /products`, compare prices for all active products
- Expected: Zero price mismatches
- Why: The user-facing price must match the exact DB value; rounding or transformation is a billing integrity issue *(catches Bug 2)*.

---

### Section 6 — Cart

**45. test_view_empty_cart**
- Input: `GET /cart` after clearing
- Expected: `200`, `items == []`
- Why: Confirms the cart endpoint returns a valid empty state after clearing.

**46. test_add_item_to_cart**
- Input: `POST /cart/add` body `{"product_id": 1, "quantity": 2}`
- Expected: `200`
- Why: Basic happy-path test for adding an item.

**47. test_add_item_quantity_zero_should_fail**
- Input: `POST /cart/add` body `{"product_id": 1, "quantity": 0}`
- Expected: `400`
- Why: Quantity must be at least 1; zero must be explicitly rejected *(catches Bug 3)*.

**48. test_add_item_negative_quantity_should_fail**
- Input: `POST /cart/add` body `{"product_id": 1, "quantity": -1}`
- Expected: `400`
- Why: Negative quantities are nonsensical and must be rejected.

**49. test_add_nonexistent_product_returns_404**
- Input: `POST /cart/add` body `{"product_id": 99999, "quantity": 1}`
- Expected: `404`
- Why: Adding a product that does not exist must return 404.

**50. test_add_more_than_stock_returns_400**
- Input: `POST /cart/add` body `{"product_id": 1, "quantity": 99999}`
- Expected: `400`
- Why: Requesting more than available stock must be refused.

**51. test_add_same_product_accumulates_quantity**
- Input: `POST /cart/add` product 1 qty 2, then again qty 3; then `GET /cart`
- Expected: One line item with `quantity == 5`
- Why: Adding the same product twice must add to the existing quantity, not create a duplicate line.

**52. test_cart_subtotal_correct**
- Input: Add product 1 qty 3; `GET /cart`
- Expected: `item.subtotal == item.quantity * item.unit_price` for every item
- Why: Subtotal integrity is critical for order totals and billing *(catches Bug 6)*.

**53. test_cart_total_is_sum_of_subtotals**
- Input: Add product 1 qty 2 and product 3 qty 4; `GET /cart`
- Expected: `cart.total == sum(qty * unit_price)` for all items
- Why: The cart total drives checkout pricing; it must reflect every item *(catches Bug 7)*.

**54. test_update_cart_item_valid**
- Input: Add product 1 qty 2; `POST /cart/update` body `{"product_id": 1, "quantity": 5}`
- Expected: `200`
- Why: Confirms the update endpoint accepts a valid new quantity.

**55. test_update_cart_item_quantity_zero_should_fail**
- Input: Add product 1; `POST /cart/update` body `{"product_id": 1, "quantity": 0}`
- Expected: `400`
- Why: Update quantity has the same minimum-1 constraint as add.

**56. test_remove_item_from_cart**
- Input: Add product 1; `POST /cart/remove` body `{"product_id": 1}`
- Expected: `200`
- Why: Basic smoke test for item removal.

**57. test_remove_item_not_in_cart_returns_404**
- Input: Clear cart; `POST /cart/remove` body `{"product_id": 1}`
- Expected: `404`
- Why: Removing a product that is not in the cart must return 404, not silently succeed.

**58. test_clear_cart**
- Input: Add product 1; `DELETE /cart/clear`; then `GET /cart`
- Expected: `200` on clear, then `items == []`
- Why: Confirms the clear endpoint fully empties the cart.

**59. test_missing_product_id_returns_400**
- Input: `POST /cart/add` body `{"quantity": 2}` — no `product_id`
- Expected: `400`
- Why: A structurally malformed request (missing required field) must be rejected with 400, not 404 *(catches Bug 4)*.

**60. test_missing_quantity_should_fail**
- Input: `POST /cart/add` body `{"product_id": 1}` — no `quantity`
- Expected: `400`
- Why: Missing quantity must be rejected, not silently defaulted to zero *(catches Bug 5)*.

**61. test_cumulative_add_exceeding_stock_should_fail**
- Input: Add product 6 qty `stock-1`; then add qty 2 (total = stock+1)
- Expected: Second call `400`
- Why: Stock enforcement must account for items already in the cart, not just the new request in isolation *(catches Bug 8)*.

**62. test_update_to_quantity_exceeding_stock_should_fail**
- Input: Add product 6 qty 1; `POST /cart/update` body `{"product_id": 6, "quantity": stock+1}`
- Expected: `400`
- Why: Updating to a quantity above stock must also be rejected *(catches Bug 9)*.

**63. test_subtotal_correct_after_multiple_adds_of_same_product**
- Input: Add product 1 qty 2, then add product 1 qty 3; `GET /cart`
- Expected: `item.subtotal == 5 * unit_price`
- Why: Subtotal must be recomputed correctly after quantity accumulation *(catches Bug 6)*.

**64. test_subtotal_correct_after_update**
- Input: Add product 1 qty 2; update to qty 7; `GET /cart`
- Expected: `item.subtotal == 7 * unit_price`
- Why: Subtotal must be recalculated when the quantity changes *(catches Bug 6)*.

---

### Section 7 — Coupons

**65. test_apply_valid_coupon**
- Input: Cart ≥ ₹500; `POST /coupon/apply` body `{"coupon_code": "PERCENT10"}`
- Expected: `200`, response has `discount` and `new_total`
- Why: Basic happy-path test confirming a valid coupon is accepted and returns the required fields.

**66. test_apply_expired_coupon_returns_400**
- Input: `POST /coupon/apply` body `{"coupon_code": "EXPIRED100"}`
- Expected: `400`
- Why: Expired coupons must be rejected; this ensures the expiry date is checked server-side.

**67. test_coupon_min_cart_value_not_met**
- Input: Cart = ₹20 (1 Water Bottle); `POST /coupon/apply` body `{"coupon_code": "PERCENT10"}` (min ₹300)
- Expected: `400`
- Why: Coupons with a minimum cart value must be rejected when the cart doesn't meet that threshold.

**68. test_coupon_max_discount_enforced**
- Input: Cart = ₹1,250 (5 Mangos); `POST /coupon/apply` body `{"coupon_code": "PERCENT10"}` (10%, max ₹100)
- Expected: `200`, `discount <= 100`
- Why: The max_discount cap must be applied; uncapped discounts overcharge the business *(catches Bug 10)*.

**69. test_fixed_coupon_discount**
- Input: Cart ≥ ₹500; `POST /coupon/apply` body `{"coupon_code": "SAVE50"}` (fixed ₹50 off)
- Expected: `200`, `discount == 50`
- Why: FIXED coupons must apply a flat deduction of exactly the specified amount.

**70. test_remove_coupon**
- Input: Apply a coupon; `POST /coupon/remove`
- Expected: `200`
- Why: Confirms the coupon removal endpoint works correctly.

**71. test_coupon_new_total_uses_real_cart_total**
- Input: 20 Water Bottles (₹400 total); `POST /coupon/apply` body `{"coupon_code": "PERCENT10"}`
- Expected: `new_total == 360` (400 − 40)
- Why: The coupon discount and new_total must be computed on the actual item total, not a bugged cart total field.

**72. test_coupon_eligibility_uses_pre_discount_cart_total**
- Input: 30 Water Bottles (real total ₹600); apply SAVE50 (new displayed total ₹550); then apply LOYALTY20 (min_cart_value ₹600)
- Expected: `200`
- Why: Coupon eligibility must check the undiscounted real total, not the post-discount displayed total.

---

### Section 8 — Checkout

**73. test_checkout_empty_cart_should_fail**
- Input: Clear cart; `POST /checkout` body `{"payment_method": "CARD"}`
- Expected: `400`
- Why: Checking out with an empty cart must be blocked *(catches Bug 11)*.

**74. test_checkout_invalid_payment_method**
- Input: `POST /checkout` body `{"payment_method": "BITCOIN"}`
- Expected: `400`
- Why: Only COD, WALLET, and CARD are valid; any other method must be rejected.

**75. test_checkout_card_payment_status_paid**
- Input: `POST /checkout` body `{"payment_method": "CARD"}`
- Expected: `200`, `payment_status == "PAID"`
- Why: Card payments are processed immediately and must start as PAID.

**76. test_checkout_cod_payment_status_pending**
- Input: `POST /checkout` body `{"payment_method": "COD"}`
- Expected: `200`, `payment_status == "PENDING"`
- Why: COD payments are not settled at checkout and must start as PENDING.

**77. test_checkout_wallet_payment_status_pending**
- Input: `POST /checkout` body `{"payment_method": "WALLET"}` for user 7
- Expected: `200`, `payment_status == "PENDING"`
- Why: Wallet payments also start as PENDING (payment is a separate step).

**78. test_checkout_cod_over_5000_should_fail**
- Input: Cart = 15 × Ghee (₹380 × 15 = ₹5,700 + GST); `POST /checkout` body `{"payment_method": "COD"}`
- Expected: `400`
- Why: COD is not allowed for orders over ₹5,000; this limit must be enforced at checkout.

**79. test_checkout_gst_5_percent**
- Input: 10 Water Bottles (₹200 subtotal); `POST /checkout` body `{"payment_method": "CARD"}`
- Expected: `gst_amount ≈ subtotal × 0.05`
- Why: GST must be exactly 5% of the pre-tax subtotal; any other rate is a billing error.

---

### Section 9 — Wallet

**80. test_view_wallet**
- Input: `GET /wallet` for user 1
- Expected: `200`, response has `wallet_balance`
- Why: Basic smoke test for the wallet endpoint.

**81. test_add_money_valid**
- Input: `POST /wallet/add` body `{"amount": 100}` for user 7; verify balance increases
- Expected: `200`, balance increases by exactly 100
- Why: Confirms money is added correctly to the wallet and the balance reflects it.

**82. test_add_money_amount_boundaries**
- Input: `POST /wallet/add` with amounts 0, −100, 100001 (each must fail); then 1 and 100000 (must succeed)
- Expected: `400` for invalid, `200` for valid
- Why: The allowed range is (0, 100000]; boundary values must be handled correctly on both sides.

**83. test_pay_invalid_amounts_should_fail**
- Input: `POST /wallet/pay` with amounts 0, −50, 999999
- Expected: All `400`
- Why: Zero and negative amounts are invalid; an amount far exceeding any wallet balance must also be rejected.

---

### Section 10 — Loyalty Points

**84. test_view_loyalty**
- Input: `GET /loyalty` for user 1
- Expected: `200`, response has `loyalty_points`
- Why: Basic smoke test for the loyalty points endpoint.

**85. test_redeem_valid**
- Input: `POST /loyalty/redeem` body `{"points": 1}`
- Expected: `200`
- Why: Redeeming the minimum valid amount (1 point) must be accepted.

**86. test_redeem_invalid_points_should_fail**
- Input: `POST /loyalty/redeem` with points 0, −5, 999999
- Expected: All `400`
- Why: Zero and negative values are invalid; exceeding the balance must also be rejected.

**87. test_redeem_exactly_full_balance_leaves_zero**
- Input: Read user 3's point balance; `POST /loyalty/redeem` body `{"points": balance}`; re-read balance
- Expected: `200`, final balance == 0
- Why: Redeeming exactly the full balance must succeed and leave the account at zero.

---

### Section 11 — Orders

**88. test_list_orders**
- Input: `GET /orders` for user 1
- Expected: `200`, list
- Why: Basic smoke test for the order list endpoint.

**89. test_get_order_detail**
- Input: `GET /orders/{id}` for user 1's first order
- Expected: `200`, response has `order_id`, `items`, `total_amount`
- Why: Confirms order detail returns the key fields needed for display and verification.

**90. test_cancel_nonexistent_order_returns_404**
- Input: `POST /orders/99999/cancel`
- Expected: `404`
- Why: Cancelling an order that does not exist must return 404.

**91. test_cancel_delivered_order_returns_400**
- Input: Find a DELIVERED order; `POST /orders/{id}/cancel`
- Expected: `400`
- Why: Delivered orders are final and must not be cancellable.

**92. test_cancel_order_restores_stock**
- Input: Order 3 × product 62; cancel; check stock before and after
- Expected: Stock returns to original level after cancellation
- Why: Cancellation must release the reserved inventory back to the product *(catches Bug 12)*.

**93. test_invoice_gst_calculation**
- Input: `GET /orders/{id}/invoice` for user 1's first order
- Expected: `subtotal + gst_amount == total_amount` and `gst_amount ≈ subtotal × 0.05`
- Why: Invoice accuracy is a legal and financial requirement; wrong GST means incorrect billing *(catches Bug 13)*.

---

### Section 12 — Reviews

**94. test_get_reviews**
- Input: `GET /products/1/reviews`
- Expected: `200`, response has `reviews` list and `average_rating`
- Why: Confirms the review endpoint returns both the list and the computed average.

**95. test_add_review_valid**
- Input: `POST /products/1/reviews` body `{"rating": 5, "comment": "Excellent product very fresh"}`
- Expected: `200` or `201`
- Why: Basic happy-path test for submitting a review.

**96. test_add_review_rating_out_of_range_should_fail**
- Input: Submit review with `rating: 0`, then `rating: 6`
- Expected: Both `400`
- Why: Ratings outside 1–5 are invalid; both boundaries must be enforced.

**97. test_add_review_comment_length_boundaries**
- Input: Submit review with empty comment `""`, then with 201-character comment
- Expected: Both `400`
- Why: Comment must be 1–200 characters; both invalid edges must be rejected.

**98. test_average_rating_is_decimal**
- Input: `GET /products/1/reviews`; compute arithmetic mean of all ratings
- Expected: `average_rating` matches computed mean within 0.01
- Why: Average must use floating-point division, not integer division which truncates fractional ratings *(catches Bug 14)*.

**99. test_no_reviews_average_is_zero**
- Input: `GET /products/250/reviews` (no reviews exist)
- Expected: `average_rating == 0`
- Why: A product with no reviews must report an average of 0, not null or an error.

---

### Section 13 — Support Tickets

**100. test_create_ticket_valid**
- Input: `POST /support/ticket` body `{"subject": "Order delivery problem", "message": "My order arrived damaged"}`
- Expected: `200`/`201`, `status == "OPEN"`, `ticket_id` present
- Why: Confirms ticket creation returns the correct initial status and an assigned ID.

**101. test_create_ticket_subject_length_boundaries**
- Input: Create ticket with `subject: "Hi"` (2 chars), then `subject: "A"*101` (101 chars)
- Expected: Both `400`
- Why: Subject must be 5–100 characters; both invalid extremes must be rejected.

**102. test_create_ticket_message_length_boundaries**
- Input: Create ticket with empty message, then with 501-character message
- Expected: Both `400`
- Why: Message must be 1–500 characters; both boundaries must be enforced.

**103. test_create_ticket_message_preserved**
- Input: `POST /support/ticket` with message `"This is my exact message with special chars: @#$%!"`
- Expected: Response `message` field equals the exact input string
- Why: The full message must be stored and returned exactly as written, including special characters.

**104. test_list_tickets**
- Input: `GET /support/tickets` for user 2
- Expected: `200`, list
- Why: Basic smoke test for the ticket list endpoint.

**105. test_ticket_status_open_to_in_progress**
- Input: Create ticket; `PUT /support/tickets/{id}` body `{"status": "IN_PROGRESS"}`
- Expected: `200`, response `status == "IN_PROGRESS"`
- Why: OPEN → IN_PROGRESS is the first valid transition and must be accepted.

**106. test_ticket_status_in_progress_to_closed**
- Input: Create ticket; advance to IN_PROGRESS; `PUT /support/tickets/{id}` body `{"status": "CLOSED"}`
- Expected: `200`, `status == "CLOSED"`
- Why: IN_PROGRESS → CLOSED is the second valid transition and must be accepted.

**107. test_ticket_status_backward_in_progress_to_open_should_fail**
- Input: Create ticket; advance to IN_PROGRESS; `PUT /support/tickets/{id}` body `{"status": "OPEN"}`
- Expected: `400`
- Why: Backward transitions must be blocked; allowing them breaks the ticket workflow *(catches Bug 15)*.

**108. test_ticket_status_closed_to_open_should_fail**
- Input: Advance ticket to CLOSED; `PUT /support/tickets/{id}` body `{"status": "OPEN"}`
- Expected: `400`
- Why: Re-opening a closed ticket is not allowed per the spec *(catches Bug 15)*.

**109. test_ticket_status_open_to_closed_should_fail**
- Input: Create ticket (OPEN); `PUT /support/tickets/{id}` body `{"status": "CLOSED"}`
- Expected: `400`
- Why: Skipping IN_PROGRESS entirely must be blocked *(catches Bug 15)*.

---

## Part 2 — Bug Report

**Bugs confirmed:** 15 server-side bugs across 13 distinct root causes

---

## Summary Table

| # | Endpoint | Root Cause | Severity |
|---|----------|-----------|----------|
| 1 | `PUT /addresses/{id}` | Update response returns old data | Medium |
| 2 | `GET /products` | Prices rounded to nearest ₹10 instead of exact DB values | High |
| 3 | `POST /cart/add` | `quantity: 0` accepted (should be 400) | Medium |
| 4 | `POST /cart/add` | Missing `product_id` returns 404 instead of 400 | Low |
| 5 | `POST /cart/add` | Missing `quantity` accepted silently with qty=0 | Medium |
| 6 | `GET /cart` | Item subtotal overflows at 255 (uint8 overflow) | Critical |
| 7 | `GET /cart` | Cart total is sum of overflowed subtotals — also wrong | Critical |
| 8 | `POST /cart/add` | Cumulative stock check not enforced across multiple calls | High |
| 9 | `POST /cart/update` | Update quantity not checked against stock | High |
| 10 | `POST /coupon/apply` | `max_discount` cap not applied to PERCENT coupons | High |
| 11 | `POST /checkout` | Empty cart checkout succeeds (should be 400) | High |
| 12 | `POST /orders/{id}/cancel` | Cancellation does not restore product stock | High |
| 13 | `GET /orders/{id}/invoice` | GST computed as 5% of total instead of 5% of subtotal | High |
| 14 | `GET /products/{id}/reviews` | `average_rating` truncated to integer (floor division) | Medium |
| 15 | `PUT /support/tickets/{id}` | Status state machine not enforced — all transitions allowed | High |

---

## Bug 1 — Address Update Response Contains Stale Data

**Endpoint:** `PUT /api/v1/addresses/{address_id}`

**Request:**
```
Method:  PUT
URL:     http://localhost:8080/api/v1/addresses/{address_id}
Headers: X-Roll-Number: 2024101126
         X-User-ID: 797
         Content-Type: application/json
Body:    {"street": "Updated Street Here"}
```

**Expected (per API doc):**
> "When an address is updated, the response must show the new updated data, not the old data."

The response body's `address.street` should equal `"Updated Street Here"`.

**Actual:**
The response returns the original street value (`"Original Street Here"`) unchanged. The underlying database record is correctly updated (confirmed by a follow-up `GET /admin/addresses` call), but the `PUT` response reflects the pre-update state.

---

## Bug 2 — Product Prices Rounded to Nearest ₹10 on User Endpoint

**Endpoint:** `GET /api/v1/products`

**Request:**
```
Method:  GET
URL:     http://localhost:8080/api/v1/products
Headers: X-Roll-Number: 2024101126
         X-User-ID: 1
```

**Expected (per API doc):**
> "The price shown for every product must be the exact real price stored in the database."

**Actual:**
154 out of ~200 active products have prices that differ from the database. The user-facing endpoint rounds all prices to the nearest ₹10, while `GET /admin/products` returns the exact stored values.

Sample mismatches:

| Product ID | DB Price (admin) | Shown Price (user) |
|-----------|------------------|--------------------|
| 8 | 95.00 | 100 |
| 10 | 45.00 | 50 |
| 70 | 185.45 | 190 |
| 71 | 123.06 | 120 |
| 72 | 48.94 | 50 |
| 75 | 24.89 | 20 |
| 250 | 284.61 | 280 |

Full mismatch count: **154 products affected**.

---

## Bug 3 — Cart Add Accepts Quantity Zero

**Endpoint:** `POST /api/v1/cart/add`

**Request:**
```
Method:  POST
URL:     http://localhost:8080/api/v1/cart/add
Headers: X-Roll-Number: 2024101126
         X-User-ID: 800
         Content-Type: application/json
Body:    {"product_id": 1, "quantity": 0}
```

**Expected (per API doc):**
> "When adding an item, the quantity must be at least 1. Sending 0 or a negative number must be rejected with a 400 error."

**Actual:**
The server returns **200 OK** and silently adds the item with `quantity: 0`. Negative quantities (e.g. `-1`) are correctly rejected with 400, but zero is not.

---

## Bug 4 — Missing `product_id` Returns 404 Instead of 400

**Endpoint:** `POST /api/v1/cart/add`

**Request:**
```
Method:  POST
URL:     http://localhost:8080/api/v1/cart/add
Headers: X-Roll-Number: 2024101126
         X-User-ID: 800
         Content-Type: application/json
Body:    {"quantity": 2}
```

**Expected (per API doc):**
A missing required field is a malformed request; the server should return **400 Bad Request**.

**Actual:**
The server returns **404 Not Found**, as if it treated the missing `product_id` as `0` or `null` and looked up a non-existent product. The correct status for a structurally invalid request is 400, not 404.

---

## Bug 5 — Missing `quantity` Field Silently Accepted

**Endpoint:** `POST /api/v1/cart/add`

**Request:**
```
Method:  POST
URL:     http://localhost:8080/api/v1/cart/add
Headers: X-Roll-Number: 2024101126
         X-User-ID: 800
         Content-Type: application/json
Body:    {"product_id": 1}
```

**Expected (per API doc):**
> "When adding an item, the quantity must be at least 1."

A request with no `quantity` field should be rejected with **400 Bad Request**.

**Actual:**
The server returns **200 OK** and adds the item to the cart, effectively using `quantity: 0`. This violates the minimum-quantity constraint and allows a zero-quantity item into the cart.

---

## Bug 6 — Cart Item Subtotal Overflows at 255 (uint8 Overflow)

**Endpoint:** `GET /api/v1/cart`

**Request:**
```
Method:  GET
URL:     http://localhost:8080/api/v1/cart
Headers: X-Roll-Number: 2024101126
         X-User-ID: 800
```
(Cart pre-loaded with product 1 at various quantities.)

**Expected (per API doc):**
> "Each item in the cart must show the correct subtotal, which is the quantity times the unit price."

| quantity | unit_price | Expected subtotal | Actual subtotal |
|----------|-----------|-------------------|-----------------|
| 3 | 120 | **360** | **104** |
| 5 | 120 | **600** | **88** |
| 7 | 120 | **840** | **72** |

**Actual:**
The subtotal field overflows once it exceeds 255. The values match `(qty × price) mod 256`, indicating the server stores or computes subtotals as an unsigned 8-bit integer (uint8). Any subtotal above ₹255 wraps around to a garbage value.

The pattern confirms this exactly:
- 3 × 120 = 360 → 360 mod 256 = **104** ✓
- 5 × 120 = 600 → 600 mod 256 = **88** ✓
- 7 × 120 = 840 → 840 mod 256 = **72** ✓

---

## Bug 7 — Cart Total Is Sum of Overflowed Subtotals

**Endpoint:** `GET /api/v1/cart`

**Request:**
```
Method:  GET
URL:     http://localhost:8080/api/v1/cart
Headers: X-Roll-Number: 2024101126
         X-User-ID: 800
```
(Cart pre-loaded with product 1 × 2 and product 3 × 4.)

**Expected:**
`cart["total"]` = sum of all `(quantity × unit_price)` = **400**

**Actual:**
`cart["total"]` = **-16**

This is a direct consequence of Bug 6: the cart total is computed as the sum of the already-overflowed subtotals. Because the subtotals are stored as int8 or uint8, they individually wrap around, and their sum yields a nonsensical (possibly negative) total.

---

## Bug 8 — Cumulative Stock Not Enforced Across Multiple `cart/add` Calls

**Endpoint:** `POST /api/v1/cart/add`

**Setup:** Product 6 has `stock_quantity = 20`.

**Request sequence:**
```
# Call 1 — adds 19 units (stock - 1); succeeds
POST /api/v1/cart/add
Body: {"product_id": 6, "quantity": 19}
→ 200 OK

# Call 2 — attempts to add 2 more (cumulative = 21 > stock = 20)
POST /api/v1/cart/add
Body: {"product_id": 6, "quantity": 2}
```

**Expected (per API doc):**
> "If the quantity asked for is more than what is in stock, the server returns a 400 error."

The second call should fail with **400** because the cumulative quantity (19 + 2 = 21) exceeds the 20-unit stock.

**Actual:**
The second call returns **200 OK**. The server only checks the quantity of the individual request (2 ≤ 20) rather than the total quantity already in the cart plus the new request.

---

## Bug 9 — Cart Update Does Not Check Stock

**Endpoint:** `POST /api/v1/cart/update`

**Setup:** Product 6 has `stock_quantity = 20`. One unit is already in the cart.

**Request:**
```
Method:  POST
URL:     http://localhost:8080/api/v1/cart/update
Headers: X-Roll-Number: 2024101126
         X-User-ID: 800
         Content-Type: application/json
Body:    {"product_id": 6, "quantity": 21}
```

**Expected (per API doc):**
Updating a cart item to a quantity that exceeds available stock should return **400**.

**Actual:**
The server returns **200 OK**, allowing the cart to hold 21 units when only 20 are in stock.

---

## Bug 10 — Coupon `max_discount` Cap Not Enforced

**Endpoint:** `POST /api/v1/coupon/apply`

**Setup:**
Cart contains 5 × product 5 (Mango Alphonso, ₹250 each) = ₹1,250 total.
Coupon `PERCENT10`: 10% off, `min_cart_value = 300`, `max_discount = 100`.

**Request:**
```
Method:  POST
URL:     http://localhost:8080/api/v1/coupon/apply
Headers: X-Roll-Number: 2024101126
         X-User-ID: 800
         Content-Type: application/json
Body:    {"coupon_code": "PERCENT10"}
```

**Expected (per API doc):**
> "If the coupon has a maximum discount cap, the discount must not go above that cap."

10% of ₹1,250 = ₹125, but `max_discount = 100`. The returned discount should be capped at **₹100**.

**Actual:**
The server returns:
```json
{"discount": 125, "new_total": 1125}
```

The `max_discount` cap is completely ignored. The uncapped 10% (₹125) is applied, exceeding the stated maximum.

---

## Bug 11 — Checkout Succeeds on Empty Cart

**Endpoint:** `POST /api/v1/checkout`

**Request:**
```
Method:  POST
URL:     http://localhost:8080/api/v1/checkout
Headers: X-Roll-Number: 2024101126
         X-User-ID: 796
         Content-Type: application/json
Body:    {"payment_method": "CARD"}
```
(Cart is empty — cleared immediately before this call.)

**Expected (per API doc):**
> "The cart must not be empty. If it is empty, the server returns a 400 error."

**Actual:**
The server returns **200 OK** and creates an order with no items. An empty-cart checkout should be rejected.

---

## Bug 12 — Order Cancellation Does Not Restore Product Stock

**Endpoint:** `POST /api/v1/orders/{order_id}/cancel`

**Setup:**
Record stock of product 62 (Water Bottle): **370 units**.
Place a CARD order for 3 × product 62. Stock drops to 367 as expected.
Then cancel the order.

**Request:**
```
Method:  POST
URL:     http://localhost:8080/api/v1/orders/{order_id}/cancel
Headers: X-Roll-Number: 2024101126
         X-User-ID: 795
```

**Expected (per API doc):**
> "When an order is cancelled, all the items in that order are added back to the product stock."

After cancellation, `stock_quantity` for product 62 should return to **370**.

**Actual:**
After cancellation, stock remains at **367**. The 3 units are never restored. The cancellation endpoint marks the order as cancelled but does not update product inventory.

---

## Bug 13 — Invoice GST Computed as 5% of Total Instead of 5% of Subtotal

**Endpoint:** `GET /api/v1/orders/{order_id}/invoice`

**Request:**
```
Method:  GET
URL:     http://localhost:8080/api/v1/orders/1209/invoice
Headers: X-Roll-Number: 2024101126
         X-User-ID: 1
```

**Response:**
```json
{
  "order_id": "1209",
  "subtotal": 1511.90,
  "gst_amount": 79.57,
  "total_amount": 1591.47
}
```

**Expected (per API doc):**
> "GST is 5 percent and is added only once."
> "The invoice shows the subtotal, the GST amount, and the total."

With subtotal = ₹1511.90:
- Correct GST = ₹1511.90 × 0.05 = **₹75.60**
- Correct total = ₹1511.90 + ₹75.60 = **₹1587.50**

**Actual:**
`gst_amount = 79.57`. Verified formula:

| Calculation | Value |
|-------------|-------|
| Expected GST (5% of subtotal) | **75.60** |
| Actual GST returned | **79.57** |
| 5% of total_amount (1591.47) | **79.57** ✓ |

The server computes GST as `total_amount × 0.05` rather than `subtotal × 0.05`. This is mathematically equivalent to treating the subtotal as the gross (GST-inclusive) price and back-calculating GST out of it using `subtotal / 0.95`, inflating the tax by a factor of `1/0.95 ≈ 1.0526`. Every invoice in the system has an overstated GST as a result.

---

## Bug 14 — Average Rating Truncated to Integer (Floor Division)

**Endpoint:** `GET /api/v1/products/{product_id}/reviews`

**Request:**
```
Method:  GET
URL:     http://localhost:8080/api/v1/products/1/reviews
Headers: X-Roll-Number: 2024101126
         X-User-ID: 1
```

**Expected (per API doc):**
> "The average rating shown must be a proper decimal calculation, not a rounded-down integer."

With ratings `[4, 4, 5, 4, 4, 4, 4, 4]` (8 reviews, sum = 33):
Expected `average_rating` = 33 / 8 = **3.875** (or 3.88 rounded to 2dp).

**Actual:**
`average_rating = 3`

The server performs integer (floor) division instead of floating-point division. Any fractional part of the average is discarded, misrepresenting product quality to users. A product with ratings `[3, 4]` would show `average_rating: 3` instead of `3.5`.

---

## Bug 15 — Support Ticket Status Machine Not Enforced

**Endpoint:** `PUT /api/v1/support/tickets/{ticket_id}`

**API doc specification:**
> "Status can only move in one direction. OPEN can go to IN_PROGRESS. IN_PROGRESS can go to CLOSED. No other changes are allowed."

Three invalid transitions were tested; all were accepted:

### 15a — Backward Transition: IN_PROGRESS → OPEN

**Request sequence:**
```
POST /support/ticket        → creates ticket T, status=OPEN
PUT  /support/tickets/T     {"status": "IN_PROGRESS"} → 200 OK  ✓
PUT  /support/tickets/T     {"status": "OPEN"}         → expected 400
```

**Actual:** Returns **200 OK**. The ticket status moves backward to OPEN.

---

### 15b — Backward Transition: CLOSED → OPEN

**Request sequence:**
```
POST /support/ticket        → creates ticket T, status=OPEN
PUT  /support/tickets/T     {"status": "IN_PROGRESS"} → 200 OK  ✓
PUT  /support/tickets/T     {"status": "CLOSED"}       → 200 OK  ✓
PUT  /support/tickets/T     {"status": "OPEN"}         → expected 400
```

**Actual:** Returns **200 OK**. A closed ticket is re-opened.

---

### 15c — Skip Transition: OPEN → CLOSED

**Request sequence:**
```
POST /support/ticket        → creates ticket T, status=OPEN
PUT  /support/tickets/T     {"status": "CLOSED"}       → expected 400
```

**Actual:** Returns **200 OK**. The ticket jumps directly from OPEN to CLOSED, bypassing IN_PROGRESS entirely.

---

The status field accepts any value regardless of the current state. The server has no state machine logic — all three forbidden transitions are silently accepted.

---

## Test Results Summary

| Section | Tests | Passed | Failed |
|---------|-------|--------|--------|
| Header Validation | 8 | 8 | 0 |
| Admin Endpoints | 12 | 12 | 0 |
| Profile | 6 | 6 | 0 |
| Addresses | 9 | 8 | 1 |
| Products | 9 | 8 | 1 |
| Cart | 20 | 11 | 9 |
| Coupons | 8 | 7 | 1 |
| Checkout | 7 | 6 | 1 |
| Wallet | 4 | 3 | 1 |
| Loyalty | 4 | 4 | 0 |
| Orders | 6 | 4 | 2 |
| Reviews | 6 | 5 | 1 |
| Support Tickets | 10 | 7 | 3 |
| **Total** | **109** | **90** | **19** |
