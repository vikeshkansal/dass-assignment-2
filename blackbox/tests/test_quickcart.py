"""
Comprehensive black-box tests for the QuickCart REST API.

Tests cover:
- Valid requests (happy paths)
- Invalid inputs, missing fields, wrong data types
- Boundary values
- Correct HTTP status codes
- Proper JSON response structures
- Correctness of returned data per API specification
"""

import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"
ROLL_NUMBER = "2024101126"


def headers(user_id=None):
    """Build request headers."""
    h = {"X-Roll-Number": ROLL_NUMBER, "Content-Type": "application/json"}
    if user_id is not None:
        h["X-User-ID"] = str(user_id)
    return h


def admin_headers():
    """Headers for admin endpoints (no X-User-ID needed)."""
    return {"X-Roll-Number": ROLL_NUMBER}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def admin_users():
    r = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers())
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="session")
def admin_products():
    r = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers())
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="session")
def admin_coupons():
    r = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers())
    assert r.status_code == 200
    return r.json()


# Use a dedicated user for tests that mutate state to avoid interference.
# Users 1-800 exist per the admin endpoint.
TEST_USER = 800
CLEAN_USER_1 = 799
CLEAN_USER_2 = 798
CLEAN_USER_3 = 797
CLEAN_USER_4 = 796
CLEAN_USER_5 = 795


def clear_cart(user_id):
    requests.delete(f"{BASE_URL}/cart/clear", headers=headers(user_id))


# =========================================================================
# 1. HEADER VALIDATION (All Requests)
# =========================================================================

class TestHeaderValidation:
    """Every request requires X-Roll-Number; user-scoped endpoints also need X-User-ID."""

    def test_missing_roll_number_returns_401(self):
        """Missing X-Roll-Number header should return 401."""
        r = requests.get(f"{BASE_URL}/admin/users")
        assert r.status_code == 401

    def test_invalid_roll_number_returns_400(self):
        """Non-integer X-Roll-Number should return 400."""
        r = requests.get(f"{BASE_URL}/admin/users", headers={"X-Roll-Number": "abc"})
        assert r.status_code == 400

    def test_missing_user_id_on_user_endpoint_returns_400(self):
        """Missing X-User-ID on user-scoped endpoint should return 400."""
        r = requests.get(f"{BASE_URL}/profile", headers=admin_headers())
        assert r.status_code == 400

    def test_invalid_user_id_returns_400(self):
        """Non-integer X-User-ID should return 400."""
        h = admin_headers()
        h["X-User-ID"] = "abc"
        r = requests.get(f"{BASE_URL}/profile", headers=h)
        assert r.status_code == 400

    def test_negative_user_id_returns_400(self):
        """Negative X-User-ID should return 400 (must be positive)."""
        r = requests.get(f"{BASE_URL}/profile", headers=headers(-1))
        assert r.status_code == 400

    def test_zero_user_id_returns_400(self):
        """Zero X-User-ID should return 400 (must be positive)."""
        r = requests.get(f"{BASE_URL}/profile", headers=headers(0))
        assert r.status_code == 400

    def test_nonexistent_user_returns_error(self):
        """X-User-ID for non-existent user should return an error."""
        r = requests.get(f"{BASE_URL}/profile", headers=headers(99999))
        assert r.status_code in (400, 404)

    def test_admin_endpoint_does_not_require_user_id(self):
        """Admin endpoints only need X-Roll-Number, not X-User-ID."""
        r = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers())
        assert r.status_code == 200


# =========================================================================
# 2. ADMIN / DATA INSPECTION
# =========================================================================

class TestAdminEndpoints:
    """Admin endpoints return full database contents."""

    def test_admin_users(self):
        r = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0
        user = data[0]
        assert "user_id" in user
        assert "name" in user
        assert "wallet_balance" in user
        assert "loyalty_points" in user

    def test_admin_users_specific(self):
        r = requests.get(f"{BASE_URL}/admin/users/1", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert data["user_id"] == 1

    def test_admin_users_nonexistent(self):
        r = requests.get(f"{BASE_URL}/admin/users/99999", headers=admin_headers())
        assert r.status_code == 404

    def test_admin_products(self):
        r = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # Should include both active and inactive
        inactive = [p for p in data if not p["is_active"]]
        assert len(inactive) > 0, "Admin products should include inactive products"

    def test_admin_carts(self):
        r = requests.get(f"{BASE_URL}/admin/carts", headers=admin_headers())
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_orders(self):
        r = requests.get(f"{BASE_URL}/admin/orders", headers=admin_headers())
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_coupons(self):
        r = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers())
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        coupon = data[0]
        assert "coupon_code" in coupon
        assert "discount_type" in coupon

    def test_admin_tickets(self):
        r = requests.get(f"{BASE_URL}/admin/tickets", headers=admin_headers())
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_addresses(self):
        r = requests.get(f"{BASE_URL}/admin/addresses", headers=admin_headers())
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_profile_update_reflected_in_admin(self):
        """After PUT /profile, GET /admin/users/{id} must show the new values."""
        user = 20
        new_name = "AdminSyncVerify"
        new_phone = "9000000001"
        requests.put(
            f"{BASE_URL}/profile",
            headers=headers(user),
            json={"name": new_name, "phone": new_phone},
        )
        admin = requests.get(
            f"{BASE_URL}/admin/users/{user}", headers=admin_headers()
        ).json()
        assert admin["name"] == new_name, (
            f"Admin should reflect updated name. Expected '{new_name}', "
            f"got '{admin['name']}'"
        )
        assert admin["phone"] == new_phone, (
            f"Admin should reflect updated phone. Expected '{new_phone}', "
            f"got '{admin['phone']}'"
        )

    def test_address_update_reflected_in_admin(self):
        """After PUT /addresses/{id}, admin/addresses must show the new street."""
        user = 21
        r = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(user),
            json={
                "label": "HOME",
                "street": "Pre Update Street",
                "city": "Surat",
                "pincode": "395001",
                "is_default": False,
            },
        )
        addr_id = r.json()["address"]["address_id"]
        new_street = "Post Update Street Here"
        requests.put(
            f"{BASE_URL}/addresses/{addr_id}",
            headers=headers(user),
            json={"street": new_street},
        )
        admin_addrs = requests.get(
            f"{BASE_URL}/admin/addresses", headers=admin_headers()
        ).json()
        match = next((a for a in admin_addrs if a["address_id"] == addr_id), None)
        assert match is not None, "Updated address should appear in admin/addresses"
        assert match["street"] == new_street, (
            f"Admin should reflect updated street. Expected '{new_street}', "
            f"got '{match.get('street')}'"
        )

    def test_user_cart_matches_admin_cart(self):
        """
        The items visible to the user in GET /cart must match the items
        visible in GET /admin/carts for that user.
        """
        user = 22
        clear_cart(user)
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(user),
            json={"product_id": 1, "quantity": 3},
        )
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(user),
            json={"product_id": 3, "quantity": 2},
        )
        user_cart = requests.get(
            f"{BASE_URL}/cart", headers=headers(user)
        ).json()
        admin_carts = requests.get(
            f"{BASE_URL}/admin/carts", headers=admin_headers()
        ).json()
        admin_cart = next(
            (c for c in admin_carts if c["user_id"] == user), None
        )
        assert admin_cart is not None, "User's cart must be visible in admin/carts"
        user_items = {i["product_id"]: i["quantity"] for i in user_cart["items"]}
        admin_items = {i["product_id"]: i["quantity"] for i in admin_cart["items"]}
        assert user_items == admin_items, (
            f"User cart items {user_items} should match admin cart items {admin_items}"
        )


# =========================================================================
# 3. PROFILE
# =========================================================================

class TestProfile:
    """Profile GET and PUT."""

    def test_get_profile(self):
        r = requests.get(f"{BASE_URL}/profile", headers=headers(1))
        assert r.status_code == 200
        data = r.json()
        assert "user_id" in data
        assert "name" in data
        assert "email" in data
        assert "phone" in data

    def test_update_profile_valid(self):
        r = requests.put(
            f"{BASE_URL}/profile",
            headers=headers(TEST_USER),
            json={"name": "Updated Name", "phone": "9876543210"},
        )
        assert r.status_code == 200

    def test_update_profile_name_length_boundaries(self):
        """Name must be between 2 and 50 characters; 1-char and 51-char must both be rejected."""
        r_short = requests.put(
            f"{BASE_URL}/profile",
            headers=headers(TEST_USER),
            json={"name": "A", "phone": "9876543210"},
        )
        assert r_short.status_code == 400, "Name of 1 char should be rejected"
        r_long = requests.put(
            f"{BASE_URL}/profile",
            headers=headers(TEST_USER),
            json={"name": "A" * 51, "phone": "9876543210"},
        )
        assert r_long.status_code == 400, "Name of 51 chars should be rejected"

    def test_update_profile_name_boundary_2_chars(self):
        """Name of exactly 2 characters should be accepted."""
        r = requests.put(
            f"{BASE_URL}/profile",
            headers=headers(TEST_USER),
            json={"name": "AB", "phone": "9876543210"},
        )
        assert r.status_code == 200

    def test_update_profile_name_boundary_50_chars(self):
        """Name of exactly 50 characters should be accepted."""
        r = requests.put(
            f"{BASE_URL}/profile",
            headers=headers(TEST_USER),
            json={"name": "A" * 50, "phone": "9876543210"},
        )
        assert r.status_code == 200

    def test_update_profile_phone_length_boundaries(self):
        """Phone must be exactly 10 digits; too short and too long must both be rejected."""
        r_short = requests.put(
            f"{BASE_URL}/profile",
            headers=headers(TEST_USER),
            json={"name": "Test", "phone": "123"},
        )
        assert r_short.status_code == 400, "Phone of 3 digits should be rejected"
        r_long = requests.put(
            f"{BASE_URL}/profile",
            headers=headers(TEST_USER),
            json={"name": "Test", "phone": "12345678901"},
        )
        assert r_long.status_code == 400, "Phone of 11 digits should be rejected"


# =========================================================================
# 4. ADDRESSES
# =========================================================================

class TestAddresses:
    """Address CRUD and validation."""

    def test_get_addresses(self):
        r = requests.get(f"{BASE_URL}/addresses", headers=headers(1))
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_address_valid(self):
        r = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(CLEAN_USER_1),
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Mumbai",
                "pincode": "400001",
                "is_default": True,
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        assert "address" in data
        addr = data["address"]
        assert "address_id" in addr
        assert addr["label"] == "HOME"
        assert addr["street"] == "123 Main Street"
        assert addr["city"] == "Mumbai"
        assert addr["pincode"] == "400001"
        assert addr["is_default"] is True

    def test_create_address_invalid_label(self):
        """Label must be HOME, OFFICE, or OTHER."""
        r = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(CLEAN_USER_1),
            json={
                "label": "WORK",
                "street": "123 Main Street",
                "city": "Mumbai",
                "pincode": "400001",
            },
        )
        assert r.status_code == 400

    def test_create_address_street_length_boundaries(self):
        """Street must be between 5 and 100 characters; too short and too long must both be rejected."""
        r_short = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(CLEAN_USER_1),
            json={"label": "HOME", "street": "ab", "city": "Mumbai", "pincode": "400001"},
        )
        assert r_short.status_code == 400, "Street of 2 chars should be rejected"
        r_long = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(CLEAN_USER_1),
            json={
                "label": "HOME",
                "street": "A" * 101,
                "city": "Mumbai",
                "pincode": "400001",
            },
        )
        assert r_long.status_code == 400, "Street of 101 chars should be rejected"

    def test_create_address_city_too_short(self):
        """City must be between 2 and 50 characters."""
        r = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(CLEAN_USER_1),
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "A",
                "pincode": "400001",
            },
        )
        assert r.status_code == 400

    def test_create_address_pincode_wrong_length(self):
        """Pincode must be exactly 6 digits."""
        r = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(CLEAN_USER_1),
            json={
                "label": "HOME",
                "street": "123 Main Street",
                "city": "Mumbai",
                "pincode": "4000",
            },
        )
        assert r.status_code == 400

    def test_create_default_address_replaces_old_default(self):
        """Adding a new default address should unset old defaults."""
        user = CLEAN_USER_2
        # Create first default
        requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(user),
            json={
                "label": "HOME",
                "street": "First Default Street",
                "city": "Delhi",
                "pincode": "110001",
                "is_default": True,
            },
        )
        # Create second default
        requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(user),
            json={
                "label": "OFFICE",
                "street": "Second Default Street",
                "city": "Delhi",
                "pincode": "110002",
                "is_default": True,
            },
        )
        # Check only one default
        r = requests.get(f"{BASE_URL}/addresses", headers=headers(user))
        addrs = r.json()
        defaults = [a for a in addrs if a["is_default"]]
        assert len(defaults) == 1, "Only one address should be default"

    def test_update_address_street(self):
        """Only street and is_default can be changed via update."""
        user = CLEAN_USER_3
        # Create address
        r = requests.post(
            f"{BASE_URL}/addresses",
            headers=headers(user),
            json={
                "label": "HOME",
                "street": "Original Street Here",
                "city": "Pune",
                "pincode": "411001",
                "is_default": False,
            },
        )
        addr_id = r.json()["address"]["address_id"]

        # Update street
        r = requests.put(
            f"{BASE_URL}/addresses/{addr_id}",
            headers=headers(user),
            json={"street": "Updated Street Here"},
        )
        assert r.status_code == 200
        # BUG CHECK: Response should show new data
        data = r.json()
        assert data["address"]["street"] == "Updated Street Here", (
            "Address update response should show the NEW updated data, not old data"
        )

    def test_delete_nonexistent_address_returns_404(self):
        r = requests.delete(
            f"{BASE_URL}/addresses/99999", headers=headers(CLEAN_USER_1)
        )
        assert r.status_code == 404



# =========================================================================
# 5. PRODUCTS
# =========================================================================

class TestProducts:
    """Product listing, filtering, sorting, and price verification."""

    def test_get_products_list(self):
        r = requests.get(f"{BASE_URL}/products", headers=headers(1))
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_products_list_excludes_inactive(self):
        """Product list should only include active products."""
        r = requests.get(f"{BASE_URL}/products", headers=headers(1))
        data = r.json()
        for p in data:
            assert p["is_active"] is True, (
                f"Inactive product {p['product_id']} should not appear in list"
            )

    def test_get_product_by_id(self):
        r = requests.get(f"{BASE_URL}/products/1", headers=headers(1))
        assert r.status_code == 200
        data = r.json()
        assert data["product_id"] == 1
        assert "name" in data
        assert "price" in data

    def test_get_nonexistent_product_returns_404(self):
        r = requests.get(f"{BASE_URL}/products/99999", headers=headers(1))
        assert r.status_code == 404

    def test_filter_by_category(self):
        r = requests.get(
            f"{BASE_URL}/products", headers=headers(1), params={"category": "Fruits"}
        )
        assert r.status_code == 200
        for p in r.json():
            assert p["category"] == "Fruits"

    def test_search_by_name(self):
        r = requests.get(
            f"{BASE_URL}/products", headers=headers(1), params={"search": "Apple"}
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0
        for p in data:
            assert "apple" in p["name"].lower()

    def test_sort_by_price_ascending(self):
        r = requests.get(
            f"{BASE_URL}/products", headers=headers(1), params={"sort": "price_asc"}
        )
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices), "Prices should be in ascending order"

    def test_sort_by_price_descending(self):
        r = requests.get(
            f"{BASE_URL}/products", headers=headers(1), params={"sort": "price_desc"}
        )
        assert r.status_code == 200
        prices = [p["price"] for p in r.json()]
        assert prices == sorted(prices, reverse=True), (
            "Prices should be in descending order"
        )

    def test_product_price_matches_database(self):
        """
        BUG TEST: The price shown for every product must be the exact real
        price stored in the database. We compare admin (DB) prices with
        user-facing prices.
        """
        admin_r = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers())
        admin_prices = {
            p["product_id"]: p["price"]
            for p in admin_r.json()
            if p.get("is_active", False)
        }

        user_r = requests.get(f"{BASE_URL}/products", headers=headers(1))
        mismatches = []
        for p in user_r.json():
            pid = p["product_id"]
            if pid in admin_prices and admin_prices[pid] != p["price"]:
                mismatches.append(
                    f"Product {pid}: admin={admin_prices[pid]}, user={p['price']}"
                )
        assert len(mismatches) == 0, (
            f"Product prices do not match database: {mismatches}"
        )


# =========================================================================
# 6. CART
# =========================================================================

class TestCart:
    """Cart operations: add, update, remove, clear, totals."""

    def setup_method(self):
        clear_cart(TEST_USER)

    def test_view_empty_cart(self):
        r = requests.get(f"{BASE_URL}/cart", headers=headers(TEST_USER))
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert data["items"] == []

    def test_add_item_to_cart(self):
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        assert r.status_code == 200

    def test_add_item_quantity_zero_should_fail(self):
        """
        BUG TEST: Quantity must be at least 1. Sending 0 must be rejected
        with a 400 error.
        """
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 0},
        )
        assert r.status_code == 400, (
            "Adding item with quantity 0 should return 400"
        )

    def test_add_item_negative_quantity_should_fail(self):
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": -1},
        )
        assert r.status_code == 400

    def test_add_nonexistent_product_returns_404(self):
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 99999, "quantity": 1},
        )
        assert r.status_code == 404

    def test_add_more_than_stock_returns_400(self):
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 99999},
        )
        assert r.status_code == 400

    def test_add_same_product_accumulates_quantity(self):
        """Adding the same product again should add to existing quantity."""
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 3},
        )
        r = requests.get(f"{BASE_URL}/cart", headers=headers(TEST_USER))
        cart = r.json()
        items = cart["items"]
        assert len(items) == 1
        assert items[0]["quantity"] == 5, (
            "Same product added twice should accumulate quantities (2+3=5)"
        )

    def test_cart_subtotal_correct(self):
        """
        BUG TEST: Each item's subtotal must equal quantity * unit_price.
        """
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 3},
        )
        r = requests.get(f"{BASE_URL}/cart", headers=headers(TEST_USER))
        cart = r.json()
        for item in cart["items"]:
            expected = item["quantity"] * item["unit_price"]
            assert item["subtotal"] == expected, (
                f"Subtotal should be {expected} (qty={item['quantity']} * "
                f"price={item['unit_price']}), got {item['subtotal']}"
            )

    def test_cart_total_is_sum_of_subtotals(self):
        """
        BUG TEST: Cart total must be the sum of all item subtotals.
        Every item must be counted, including the last one.
        """
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 3, "quantity": 4},
        )
        r = requests.get(f"{BASE_URL}/cart", headers=headers(TEST_USER))
        cart = r.json()
        expected_total = sum(
            item["quantity"] * item["unit_price"] for item in cart["items"]
        )
        assert cart["total"] == expected_total, (
            f"Cart total should be {expected_total}, got {cart['total']}"
        )

    def test_update_cart_item_valid(self):
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        r = requests.post(
            f"{BASE_URL}/cart/update",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 5},
        )
        assert r.status_code == 200

    def test_update_cart_item_quantity_zero_should_fail(self):
        """Update quantity must be at least 1."""
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        r = requests.post(
            f"{BASE_URL}/cart/update",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 0},
        )
        assert r.status_code == 400

    def test_remove_item_from_cart(self):
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        r = requests.post(
            f"{BASE_URL}/cart/remove",
            headers=headers(TEST_USER),
            json={"product_id": 1},
        )
        assert r.status_code == 200

    def test_remove_item_not_in_cart_returns_404(self):
        """
        BUG TEST: Removing a product not in the cart should return 404.
        """
        r = requests.post(
            f"{BASE_URL}/cart/remove",
            headers=headers(TEST_USER),
            json={"product_id": 1},
        )
        assert r.status_code == 404, (
            "Removing a product not in the cart should return 404"
        )

    def test_clear_cart(self):
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 1},
        )
        r = requests.delete(f"{BASE_URL}/cart/clear", headers=headers(TEST_USER))
        assert r.status_code == 200
        cart = requests.get(f"{BASE_URL}/cart", headers=headers(TEST_USER)).json()
        assert cart["items"] == []

    def test_missing_product_id_returns_400(self):
        """
        BUG TEST: Sending a cart/add request with no product_id field should
        return 400 (bad request). The server currently returns 404 by treating
        the missing field as product ID 0 / null.
        """
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"quantity": 2},
        )
        assert r.status_code == 400, (
            "Missing product_id should return 400, not 404"
        )

    def test_missing_quantity_should_fail(self):
        """
        BUG TEST: Sending a cart/add request with no quantity field should
        return 400. The server currently adds the item with quantity=0.
        """
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1},
        )
        assert r.status_code == 400, (
            "Missing quantity should return 400, not silently add with qty=0"
        )

    def test_cumulative_add_exceeding_stock_should_fail(self):
        """
        BUG TEST: Adding items in multiple calls where the running total exceeds
        available stock should fail. E.g. stock=20, add 19, then add 2 more
        (total 21) should return 400.
        """
        product_id = 6
        stock = requests.get(
            f"{BASE_URL}/products/{product_id}", headers=headers(TEST_USER)
        ).json()["stock_quantity"]
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": product_id, "quantity": stock - 1},
        )
        r = requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": product_id, "quantity": 2},
        )
        assert r.status_code == 400, (
            f"Cumulative quantity ({stock - 1} + 2 = {stock + 1}) exceeds "
            f"stock ({stock}) and should return 400"
        )

    def test_update_to_quantity_exceeding_stock_should_fail(self):
        """
        BUG TEST: Updating a cart item to a quantity above available stock
        should return 400.
        """
        product_id = 6
        stock = requests.get(
            f"{BASE_URL}/products/{product_id}", headers=headers(TEST_USER)
        ).json()["stock_quantity"]
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": product_id, "quantity": 1},
        )
        r = requests.post(
            f"{BASE_URL}/cart/update",
            headers=headers(TEST_USER),
            json={"product_id": product_id, "quantity": stock + 1},
        )
        assert r.status_code == 400, (
            f"Updating quantity to {stock + 1} exceeds stock ({stock}) "
            "and should return 400"
        )

    def test_subtotal_correct_after_multiple_adds_of_same_product(self):
        """
        BUG TEST: Each item subtotal must equal quantity * unit_price even
        after the same product has been added in multiple separate calls.
        """
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 3},
        )
        cart = requests.get(f"{BASE_URL}/cart", headers=headers(TEST_USER)).json()
        for item in cart["items"]:
            expected = item["quantity"] * item["unit_price"]
            assert item["subtotal"] == expected, (
                f"After two adds of the same product, subtotal should be "
                f"{expected} (qty={item['quantity']} * price={item['unit_price']}), "
                f"got {item['subtotal']}"
            )

    def test_subtotal_correct_after_update(self):
        """
        BUG TEST: Subtotal must be recalculated correctly after a cart update.
        """
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 2},
        )
        requests.post(
            f"{BASE_URL}/cart/update",
            headers=headers(TEST_USER),
            json={"product_id": 1, "quantity": 7},
        )
        cart = requests.get(f"{BASE_URL}/cart", headers=headers(TEST_USER)).json()
        for item in cart["items"]:
            expected = item["quantity"] * item["unit_price"]
            assert item["subtotal"] == expected, (
                f"After update, subtotal should be {expected} "
                f"(qty={item['quantity']} * price={item['unit_price']}), "
                f"got {item['subtotal']}"
            )


# =========================================================================
# 7. COUPONS
# =========================================================================

class TestCoupons:
    """Coupon apply and remove."""

    def setup_method(self):
        clear_cart(TEST_USER)
        # Remove any existing coupon
        requests.post(f"{BASE_URL}/coupon/remove", headers=headers(TEST_USER))

    def _add_items_for_coupon(self, total_needed):
        """Add items to cart to reach a certain approximate total."""
        # Product 5 (Mango Alphonso) = 250 per unit
        qty = max(1, total_needed // 250 + 1)
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 5, "quantity": qty},
        )

    def test_apply_valid_coupon(self):
        """PERCENT10: 10% off, min 300, max discount 100."""
        self._add_items_for_coupon(500)
        r = requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "PERCENT10"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "discount" in data
        assert "new_total" in data

    def test_apply_expired_coupon_returns_400(self):
        """EXPIRED100 is expired."""
        self._add_items_for_coupon(2000)
        r = requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "EXPIRED100"},
        )
        assert r.status_code == 400

    def test_coupon_min_cart_value_not_met(self):
        """Cart total below minimum should fail."""
        # Add only 1 cheap item (product 62, Water Bottle = 20)
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 62, "quantity": 1},
        )
        r = requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "PERCENT10"},  # min_cart_value=300
        )
        assert r.status_code == 400

    def test_coupon_max_discount_enforced(self):
        """
        BUG TEST: PERCENT10 is 10% off with max_discount=100.
        If cart is 1250, 10% = 125, but capped at 100.
        """
        # Add 5 Mangos (250 each) = 1250
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 5, "quantity": 5},
        )
        r = requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "PERCENT10"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["discount"] <= 100, (
            f"Discount {data['discount']} exceeds max_discount cap of 100"
        )

    def test_fixed_coupon_discount(self):
        """SAVE50: fixed 50 off, min 500, max 50."""
        self._add_items_for_coupon(600)
        r = requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "SAVE50"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["discount"] == 50

    def test_remove_coupon(self):
        self._add_items_for_coupon(500)
        requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "SAVE50"},
        )
        r = requests.post(f"{BASE_URL}/coupon/remove", headers=headers(TEST_USER))
        assert r.status_code == 200

    def test_coupon_new_total_uses_real_cart_total(self):
        """
        BUG TEST: Even though the cart's displayed total is wrong (bug), the
        coupon's new_total must be computed from the real item total
        (sum of qty * unit_price). Verified against the correct expected value.
        """
        # 20 Water Bottles x 20 = 400 real total
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 62, "quantity": 20},
        )
        r = requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "PERCENT10"},  # 10% off, max 100
        )
        data = r.json()
        assert r.status_code == 200
        real_total = 20 * 20  # qty * price
        discount = min(real_total * 0.10, 100)
        expected_new_total = real_total - discount
        assert abs(data["new_total"] - expected_new_total) < 0.02, (
            f"new_total should be {expected_new_total} "
            f"(real_total={real_total} - discount={discount}), "
            f"got {data['new_total']}"
        )

    def test_coupon_eligibility_uses_pre_discount_cart_total(self):
        """
        When a coupon is already applied and a second coupon is applied to
        replace it, eligibility (min_cart_value) must be checked against the
        real undiscounted cart total — not the post-discount total of the
        previous coupon.

        Setup: real cart = 600 (30 x 20).
        Apply SAVE50 first (min=500) -> new_total=550.
        Then apply LOYALTY20 (min=600). Real total 600 >= 600, so it should succeed.
        """
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(TEST_USER),
            json={"product_id": 62, "quantity": 30},
        )
        requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "SAVE50"},
        )
        r = requests.post(
            f"{BASE_URL}/coupon/apply",
            headers=headers(TEST_USER),
            json={"coupon_code": "LOYALTY20"},
        )
        assert r.status_code == 200, (
            "LOYALTY20 (min=600) should be accepted when real cart total=600, "
            "even if a prior coupon brought the displayed total to 550"
        )


# =========================================================================
# 8. CHECKOUT
# =========================================================================

class TestCheckout:
    """Checkout with various payment methods."""

    def _setup_cart(self, user_id, product_id=62, quantity=1):
        """Set up a cart with one item for checkout."""
        clear_cart(user_id)
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(user_id),
            json={"product_id": product_id, "quantity": quantity},
        )

    def test_checkout_empty_cart_should_fail(self):
        """
        BUG TEST: Empty cart checkout should return 400.
        """
        user = CLEAN_USER_4
        clear_cart(user)
        r = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "CARD"},
        )
        assert r.status_code == 400, (
            "Checkout with empty cart should return 400"
        )

    def test_checkout_invalid_payment_method(self):
        user = CLEAN_USER_4
        self._setup_cart(user)
        r = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "BITCOIN"},
        )
        assert r.status_code == 400

    def test_checkout_card_payment_status_paid(self):
        """CARD payment should start with payment_status PAID."""
        user = CLEAN_USER_4
        self._setup_cart(user)
        r = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "CARD"},
        )
        assert r.status_code == 200
        assert r.json()["payment_status"] == "PAID"

    def test_checkout_cod_payment_status_pending(self):
        """COD payment should start with payment_status PENDING."""
        user = CLEAN_USER_4
        self._setup_cart(user)
        r = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "COD"},
        )
        assert r.status_code == 200
        assert r.json()["payment_status"] == "PENDING"

    def test_checkout_wallet_payment_status_pending(self):
        """WALLET payment should start with payment_status PENDING."""
        user = 7  # Has high wallet balance
        self._setup_cart(user)
        r = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "WALLET"},
        )
        assert r.status_code == 200
        assert r.json()["payment_status"] == "PENDING"

    def test_checkout_cod_over_5000_should_fail(self):
        """COD not allowed if order total > 5000."""
        user = CLEAN_USER_4
        clear_cart(user)
        # Product 42 (Ghee) = 380/unit, 15 units = 5700 + GST > 5000
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(user),
            json={"product_id": 42, "quantity": 15},
        )
        r = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "COD"},
        )
        assert r.status_code == 400

    def test_checkout_gst_5_percent(self):
        """Total should include exactly 5% GST."""
        user = CLEAN_USER_4
        self._setup_cart(user, product_id=62, quantity=10)  # 10 * 20 = 200
        r = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "CARD"},
        )
        data = r.json()
        # With 5% GST: total = subtotal * 1.05
        gst = data["gst_amount"]
        total = data["total_amount"]
        subtotal = total - gst
        expected_gst = round(subtotal * 0.05, 2)
        assert abs(gst - expected_gst) < 0.02, (
            f"GST should be 5% of subtotal. Expected {expected_gst}, got {gst}"
        )


# =========================================================================
# 9. WALLET
# =========================================================================

class TestWallet:
    """Wallet view, add, and pay."""

    def test_view_wallet(self):
        r = requests.get(f"{BASE_URL}/wallet", headers=headers(1))
        assert r.status_code == 200
        assert "wallet_balance" in r.json()

    def test_add_money_valid(self):
        user = 7  # Has initial balance
        before = requests.get(f"{BASE_URL}/wallet", headers=headers(user)).json()[
            "wallet_balance"
        ]
        r = requests.post(
            f"{BASE_URL}/wallet/add",
            headers=headers(user),
            json={"amount": 100},
        )
        assert r.status_code == 200
        after = requests.get(f"{BASE_URL}/wallet", headers=headers(user)).json()[
            "wallet_balance"
        ]
        assert abs(after - (before + 100)) < 0.01, (
            f"Balance should increase by exactly 100: {before} + 100 = {before + 100}, got {after}"
        )

    def test_add_money_amount_boundaries(self):
        """Amount must be > 0 and <= 100000. Zero, negative, and over-limit must fail; 1 and 100000 must succeed."""
        for bad in [0, -100, 100001]:
            r = requests.post(
                f"{BASE_URL}/wallet/add",
                headers=headers(1),
                json={"amount": bad},
            )
            assert r.status_code == 400, f"Amount {bad} should be rejected"
        for good in [1, 100000]:
            r = requests.post(
                f"{BASE_URL}/wallet/add",
                headers=headers(1),
                json={"amount": good},
            )
            assert r.status_code == 200, f"Amount {good} should be accepted"

    def test_pay_invalid_amounts_should_fail(self):
        """Pay amount must be > 0 and not exceed balance; zero, negative, and over-balance must all fail."""
        for bad in [0, -50, 999999]:
            r = requests.post(
                f"{BASE_URL}/wallet/pay",
                headers=headers(1),
                json={"amount": bad},
            )
            assert r.status_code == 400, f"Pay amount {bad} should be rejected"



# =========================================================================
# 10. LOYALTY POINTS
# =========================================================================

class TestLoyalty:
    """Loyalty points view and redeem."""

    def test_view_loyalty(self):
        r = requests.get(f"{BASE_URL}/loyalty", headers=headers(1))
        assert r.status_code == 200
        assert "loyalty_points" in r.json()

    def test_redeem_valid(self):
        r = requests.post(
            f"{BASE_URL}/loyalty/redeem",
            headers=headers(1),
            json={"points": 1},
        )
        assert r.status_code == 200

    def test_redeem_invalid_points_should_fail(self):
        """Redeeming zero, negative, or more points than balance must all be rejected."""
        for bad in [0, -5, 999999]:
            r = requests.post(
                f"{BASE_URL}/loyalty/redeem",
                headers=headers(1),
                json={"points": bad},
            )
            assert r.status_code == 400, f"Redeeming {bad} points should be rejected"

    def test_redeem_exactly_full_balance_leaves_zero(self):
        """Redeeming exactly all loyalty points should succeed and leave 0."""
        user = 3
        points = requests.get(
            f"{BASE_URL}/loyalty", headers=headers(user)
        ).json()["loyalty_points"]
        r = requests.post(
            f"{BASE_URL}/loyalty/redeem",
            headers=headers(user),
            json={"points": points},
        )
        assert r.status_code == 200
        after = requests.get(
            f"{BASE_URL}/loyalty", headers=headers(user)
        ).json()["loyalty_points"]
        assert after == 0, (
            f"After redeeming full balance ({points} points), "
            f"loyalty_points should be 0, got {after}"
        )


# =========================================================================
# 11. ORDERS
# =========================================================================

class TestOrders:
    """Order list, detail, cancel, and invoice."""

    def test_list_orders(self):
        r = requests.get(f"{BASE_URL}/orders", headers=headers(1))
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_order_detail(self):
        # Get first order of user 1
        orders = requests.get(f"{BASE_URL}/orders", headers=headers(1)).json()
        if orders:
            oid = orders[0]["order_id"]
            r = requests.get(f"{BASE_URL}/orders/{oid}", headers=headers(1))
            assert r.status_code == 200
            data = r.json()
            assert "order_id" in data
            assert "items" in data
            assert "total_amount" in data

    def test_cancel_nonexistent_order_returns_404(self):
        r = requests.post(
            f"{BASE_URL}/orders/99999/cancel", headers=headers(1)
        )
        assert r.status_code == 404

    def test_cancel_delivered_order_returns_400(self):
        """A delivered order cannot be cancelled."""
        orders = requests.get(f"{BASE_URL}/orders", headers=headers(1)).json()
        delivered = [o for o in orders if o["order_status"] == "DELIVERED"]
        if delivered:
            oid = delivered[0]["order_id"]
            r = requests.post(
                f"{BASE_URL}/orders/{oid}/cancel", headers=headers(1)
            )
            assert r.status_code == 400

    def test_cancel_order_restores_stock(self):
        """
        BUG TEST: Cancelling an order should restore product stock.
        """
        user = CLEAN_USER_5
        product_id = 62  # Water Bottle

        # Get stock before
        stock_before = requests.get(
            f"{BASE_URL}/products/{product_id}", headers=headers(user)
        ).json()["stock_quantity"]

        # Create order
        clear_cart(user)
        requests.post(
            f"{BASE_URL}/cart/add",
            headers=headers(user),
            json={"product_id": product_id, "quantity": 3},
        )
        checkout = requests.post(
            f"{BASE_URL}/checkout",
            headers=headers(user),
            json={"payment_method": "CARD"},
        ).json()
        order_id = checkout["order_id"]

        stock_after_order = requests.get(
            f"{BASE_URL}/products/{product_id}", headers=headers(user)
        ).json()["stock_quantity"]
        assert stock_after_order == stock_before - 3

        # Cancel order
        requests.post(
            f"{BASE_URL}/orders/{order_id}/cancel", headers=headers(user)
        )

        stock_after_cancel = requests.get(
            f"{BASE_URL}/products/{product_id}", headers=headers(user)
        ).json()["stock_quantity"]
        assert stock_after_cancel == stock_before, (
            f"Stock should be restored after cancellation. "
            f"Before order: {stock_before}, after cancel: {stock_after_cancel}"
        )

    def test_invoice_gst_calculation(self):
        """
        BUG TEST: Invoice GST must be exactly 5% of subtotal.
        subtotal + GST = total.
        """
        orders = requests.get(f"{BASE_URL}/orders", headers=headers(1)).json()
        if orders:
            oid = orders[0]["order_id"]
            r = requests.get(
                f"{BASE_URL}/orders/{oid}/invoice", headers=headers(1)
            )
            assert r.status_code == 200
            inv = r.json()
            assert "subtotal" in inv
            assert "gst_amount" in inv
            assert "total_amount" in inv

            # subtotal + gst = total
            assert abs(
                (inv["subtotal"] + inv["gst_amount"]) - inv["total_amount"]
            ) < 0.01, "subtotal + GST should equal total"

            # GST = 5% of subtotal
            expected_gst = round(inv["subtotal"] * 0.05, 2)
            assert abs(inv["gst_amount"] - expected_gst) < 0.02, (
                f"GST should be 5% of subtotal ({inv['subtotal']}). "
                f"Expected: {expected_gst}, got: {inv['gst_amount']}"
            )


# =========================================================================
# 12. REVIEWS
# =========================================================================

class TestReviews:
    """Product reviews."""

    def test_get_reviews(self):
        r = requests.get(f"{BASE_URL}/products/1/reviews", headers=headers(1))
        assert r.status_code == 200
        data = r.json()
        assert "reviews" in data
        assert "average_rating" in data

    def test_add_review_valid(self):
        r = requests.post(
            f"{BASE_URL}/products/1/reviews",
            headers=headers(2),
            json={"rating": 5, "comment": "Excellent product very fresh"},
        )
        assert r.status_code in (200, 201)

    def test_add_review_rating_out_of_range_should_fail(self):
        """Rating must be between 1 and 5; 0 and 6 must both be rejected."""
        r_low = requests.post(
            f"{BASE_URL}/products/1/reviews",
            headers=headers(1),
            json={"rating": 0, "comment": "Bad product"},
        )
        assert r_low.status_code == 400, "Rating of 0 should be rejected"
        r_high = requests.post(
            f"{BASE_URL}/products/1/reviews",
            headers=headers(1),
            json={"rating": 6, "comment": "Great product"},
        )
        assert r_high.status_code == 400, "Rating of 6 should be rejected"

    def test_add_review_comment_length_boundaries(self):
        """Comment must be between 1 and 200 characters; empty and 201-char must both be rejected."""
        r_empty = requests.post(
            f"{BASE_URL}/products/1/reviews",
            headers=headers(1),
            json={"rating": 3, "comment": ""},
        )
        assert r_empty.status_code == 400, "Empty comment should be rejected"
        r_long = requests.post(
            f"{BASE_URL}/products/1/reviews",
            headers=headers(1),
            json={"rating": 3, "comment": "A" * 201},
        )
        assert r_long.status_code == 400, "Comment of 201 chars should be rejected"

    def test_average_rating_is_decimal(self):
        """
        BUG TEST: Average rating must be a proper decimal, not a
        rounded-down integer.
        """
        r = requests.get(f"{BASE_URL}/products/1/reviews", headers=headers(1))
        data = r.json()
        reviews = data["reviews"]
        if reviews:
            ratings = [rv["rating"] for rv in reviews]
            expected_avg = sum(ratings) / len(ratings)
            actual_avg = data["average_rating"]
            assert abs(actual_avg - expected_avg) < 0.01, (
                f"Average rating should be {expected_avg:.2f} "
                f"(decimal), got {actual_avg}"
            )

    def test_no_reviews_average_is_zero(self):
        """If a product has no reviews, average_rating should be 0."""
        # Find a product with no reviews by checking a high-numbered product
        # We add a review to a fresh product to verify the behavior first
        # Check product 250
        r = requests.get(f"{BASE_URL}/products/250/reviews", headers=headers(1))
        data = r.json()
        if len(data["reviews"]) == 0:
            assert data["average_rating"] == 0


# =========================================================================
# 13. SUPPORT TICKETS
# =========================================================================

class TestSupportTickets:
    """Support ticket create, list, and status update."""

    def test_create_ticket_valid(self):
        r = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(2),
            json={
                "subject": "Order delivery problem",
                "message": "My order arrived damaged",
            },
        )
        assert r.status_code in (200, 201)
        data = r.json()
        assert data["status"] == "OPEN"
        assert "ticket_id" in data

    def test_create_ticket_subject_length_boundaries(self):
        """Subject must be between 5 and 100 characters; too short and too long must both be rejected."""
        r_short = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(1),
            json={"subject": "Hi", "message": "Some message here"},
        )
        assert r_short.status_code == 400, "Subject of 2 chars should be rejected"
        r_long = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(1),
            json={"subject": "A" * 101, "message": "Some message here"},
        )
        assert r_long.status_code == 400, "Subject of 101 chars should be rejected"

    def test_create_ticket_message_length_boundaries(self):
        """Message must be between 1 and 500 characters; empty and 501-char must both be rejected."""
        r_empty = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(1),
            json={"subject": "Valid subject here", "message": ""},
        )
        assert r_empty.status_code == 400, "Empty message should be rejected"
        r_long = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(1),
            json={"subject": "Valid subject here", "message": "A" * 501},
        )
        assert r_long.status_code == 400, "Message of 501 chars should be rejected"

    def test_create_ticket_message_preserved(self):
        """Full message must be saved exactly as written."""
        msg = "This is my exact message with special chars: @#$%!"
        r = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(3),
            json={"subject": "Test message preservation", "message": msg},
        )
        data = r.json()
        assert data.get("message") == msg, (
            f"Message should be preserved exactly. Expected: '{msg}', got: '{data.get('message')}'"
        )

    def test_list_tickets(self):
        r = requests.get(f"{BASE_URL}/support/tickets", headers=headers(2))
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_ticket_status_open_to_in_progress(self):
        """OPEN -> IN_PROGRESS is valid."""
        r = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(4),
            json={"subject": "Status test ticket", "message": "Testing status"},
        )
        tid = r.json()["ticket_id"]
        r = requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(4),
            json={"status": "IN_PROGRESS"},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "IN_PROGRESS"

    def test_ticket_status_in_progress_to_closed(self):
        """IN_PROGRESS -> CLOSED is valid."""
        r = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(5),
            json={"subject": "Close test ticket", "message": "Testing close"},
        )
        tid = r.json()["ticket_id"]
        requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(5),
            json={"status": "IN_PROGRESS"},
        )
        r = requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(5),
            json={"status": "CLOSED"},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "CLOSED"

    def test_ticket_status_backward_in_progress_to_open_should_fail(self):
        """
        BUG TEST: IN_PROGRESS -> OPEN is not allowed.
        """
        r = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(6),
            json={"subject": "Backward test ticket", "message": "Testing backward"},
        )
        tid = r.json()["ticket_id"]
        requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(6),
            json={"status": "IN_PROGRESS"},
        )
        r = requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(6),
            json={"status": "OPEN"},
        )
        assert r.status_code == 400, (
            "Status transition IN_PROGRESS -> OPEN should not be allowed"
        )

    def test_ticket_status_closed_to_open_should_fail(self):
        """
        BUG TEST: CLOSED -> OPEN is not allowed.
        """
        r = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(8),
            json={"subject": "Closed backward test", "message": "Testing closed"},
        )
        tid = r.json()["ticket_id"]
        requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(8),
            json={"status": "IN_PROGRESS"},
        )
        requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(8),
            json={"status": "CLOSED"},
        )
        r = requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(8),
            json={"status": "OPEN"},
        )
        assert r.status_code == 400, (
            "Status transition CLOSED -> OPEN should not be allowed"
        )

    def test_ticket_status_open_to_closed_should_fail(self):
        """OPEN -> CLOSED directly is not allowed (must go through IN_PROGRESS)."""
        r = requests.post(
            f"{BASE_URL}/support/ticket",
            headers=headers(9),
            json={"subject": "Skip status test", "message": "Testing skip"},
        )
        tid = r.json()["ticket_id"]
        r = requests.put(
            f"{BASE_URL}/support/tickets/{tid}",
            headers=headers(9),
            json={"status": "CLOSED"},
        )
        assert r.status_code == 400, (
            "Status transition OPEN -> CLOSED directly should not be allowed"
        )

