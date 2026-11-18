(() => {
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const money = (amount) => new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(amount || 0);
  const iconPaths = {
    chef: '<path d="M6 19h12M8 19v3h8v-3M5 11a4 4 0 0 1 2.4-7.2A5.5 5.5 0 0 1 17.8 5 3.5 3.5 0 0 1 19 12H5z"/>',
    home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
    utensils: '<path d="M4 3v7a3 3 0 0 0 6 0V3M7 3v18M17 3v18M17 3c-2 2-3 5-3 8h6V3z"/>',
    receipt: '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6M9 16h3"/>',
    ticket: '<path d="M4 6h16v4a2 2 0 0 0 0 4v4H4v-4a2 2 0 0 0 0-4zM12 7v2m0 3v2m0 3v1"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M5 21v-2a7 7 0 0 1 14 0v2z"/>',
    search: '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/>',
    "map-pin": '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="2.5"/>',
    building: '<path d="M4 21V5l8-3 8 3v16M2 21h20M8 8h1m6 0h1M8 12h1m6 0h1M10 21v-5h4v5"/>',
    book: '<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v18H6.5A2.5 2.5 0 0 0 4 22zM4 4.5v15A2.5 2.5 0 0 1 6.5 17H20M8 6h8"/>',
    grill: '<path d="M4 5h16M6 9h12l-1 9H7zM9 18v3m6-3v3M8 2v3m4-3v3m4-3v3"/>',
    rolls: '<path d="M4 8c0-2 3.6-4 8-4s8 2 8 4-3.6 4-8 4-8-2-8-4zM4 8v8c0 2 3.6 4 8 4s8-2 8-4V8M8 11v8m8-8v8"/>',
    noodles: '<path d="M3 12h18a9 9 0 0 1-18 0zM5 8c0-3 2-5 2-7m4 7c0-3 2-5 2-7m4 7c0-3 2-5 2-7"/>',
    rice: '<path d="M4 12h16a8 8 0 0 1-16 0zM3 12h18M8 8c0-2 2-3 4-3s4 1 4 3M7 18h10"/>',
    restaurant: '<path d="M3 21h18M5 21V8l7-5 7 5v13M9 21v-6h6v6M8 10h.01M16 10h.01"/>',
    logout: '<path d="M10 17l5-5-5-5m5 5H3m9-9h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/>',
    "arrow-left": '<path d="m15 18-6-6 6-6M9 12h12"/>',
    "arrow-right": '<path d="M3 12h18m-7-7 7 7-7 7"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    refresh: '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.5 9A7 7 0 0 1 18 6l2 2M4 16l2 2a7 7 0 0 0 12.5-3"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    minus: '<path d="M5 12h14"/>',
    close: '<path d="m6 6 12 12M18 6 6 18"/>',
    food: '<path d="M3 11h18a9 9 0 0 1-18 0zM5 7a8 8 0 0 1 14 0M12 3v2"/>'
  };
  function icon(name, className = "icon") { return `<svg class="${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.food}</svg>`; }
  function hydrateIcons(root = document) { root.querySelectorAll("[data-icon]").forEach((node) => { node.innerHTML = icon(node.dataset.icon, "icon"); }); }
  const copy = {
    en: {
      tagline:"GOOD FOOD, CLOSE BY",home:"Home",order_food:"Order Food",my_orders:"My Orders",vouchers:"Vouchers",profile:"Profile",footer_tagline:"Freshly made.\nHappily delivered.",hello:"Hello,",customer_account:"Customer account",logout:"Log out",nearby_label:"NEARBY RESTAURANTS",hero_title:"What are you craving today?",hero_subtitle:"Choose a nearby restaurant and explore its menu.",search_placeholder:"Search restaurants...",search_hint:"Search by name or location",restaurants:"NEARBY RESTAURANTS",restaurant_data_note:'Real restaurant locations based on <a href="https://international.tdtu.edu.vn/en/support/surrounding" target="_blank" rel="noreferrer">TDTU information</a>. Menus, prices and delivery availability are demo data.',menu_demo_note:"Sample menu and prices for this demo. They may differ from the restaurant's current menu.",your_cart:"Your Cart",view_cart:"View cart",cart_subtitle:"Review your items before placing the order.",order_summary:"Order Summary",subtotal:"Subtotal",total:"Total",delivery_fee_not_included:"Delivery fee is not included.",continue_checkout:"Continue to Checkout",checkout_title:"Checkout",checkout_subtitle:"A few details and your restaurant will get cooking.",delivery_information:"Delivery Information",delivery_address:"Delivery address",address_placeholder:"Street, building, apartment...",recipient_name:"Recipient name",name_placeholder:"Your name",phone_number:"Phone number",note_optional:"Note (optional)",note_placeholder:"For example: call when you arrive",voucher:"Voucher",voucher_placeholder:"Enter voucher code",apply:"Apply",voucher_unavailable:"Voucher validation is not connected yet.",payment_method:"Payment Method",cod:"Cash on Delivery (COD)",delivery_fee:"Delivery fee",not_calculated:"Not calculated",discount:"Discount",delivery_fee_note:"Delivery fee is not included in this demo.",place_order:"Place Order",order_success_eyebrow:"ORDER PLACED SUCCESSFULLY",order_success_title:"Your order is on its way!",order_number:"Order number",order_success_message:"The restaurant will confirm and prepare your order.",restaurant:"Restaurant",order_total:"Order total",status:"Status",order_status_message:"Your order status will update when the restaurant confirms.",order_again:"Order Again",track_order:"Track Order",placeholder_prompt:"Choose",placeholder_suffix:"to browse nearby restaurants.",search_empty:"No restaurants match your search.",view_menu:"View menu",on_campus:"Nearby restaurant",menu_sample:"Sample menu",add:"Add",all:"All",items:"items",item:"item",placed_from:"ORDER FROM",empty_cart:"Your cart is empty. Add a dish to continue.",empty_cart_short:"Your cart is empty.",demo_error:"This feature is not connected yet.",cancel_hub_change:"Changing restaurants will clear the current cart. Continue?",choose_items:"Choose a restaurant and add at least one item.",placing:"Placing order...",track_pending:"Order {id} is PENDING. Order tracking is part of UC02.",load_error:"Unable to load restaurants",no_menu:"No sample menu is available for this restaurant.",main_dish:"Main dish",side_dish:"Side dish",drink:"Drinks"
    }
  };
  let language = "en";
  const t = (key) => copy[language][key] || copy.en[key] || key;
  const state = { hubs: [], hub: null, menu: [], category: "All", cart: {}, cartHubId: Number(sessionStorage.getItem("saigonbite-cart-hub")) || null, lastOrder: null, screen: "hub", user: null, customerOrders: [] };
  const savedCart = sessionStorage.getItem("saigonbite-cart");
  if (savedCart) {
    try { Object.assign(state.cart, JSON.parse(savedCart)); } catch { sessionStorage.removeItem("saigonbite-cart"); }
  }

  async function api(url, options = {}) {
    const response = await fetch(url, { credentials: "same-origin", ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
      if (response.status === 401) location.assign("/");
      throw new Error(data?.detail || "Something went wrong. Please try again.");
    }
    return data;
  }

  function showNotice(message, kind = "warning") {
    const notice = $("#notice");
    notice.className = `alert alert-${kind}`;
    notice.textContent = message;
    notice.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  function clearNotice() { $("#notice").className = "alert d-none"; }
  function toggleScreen(name) {
    ["hub", "menu", "cart", "checkout", "success"].forEach((screen) => $(`#${screen}-screen`)?.classList.toggle("d-none", screen !== name));
    state.screen = name;
    clearNotice();
  }
  function escapeHtml(value) { return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]); }

  function applyLanguage() {
    document.documentElement.lang = language;
    document.title = "Order Food | SaigonBite";
    $$('[data-i18n]').forEach((node) => { node.textContent = t(node.dataset.i18n); });
    $$('[data-i18n-placeholder]').forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
    $$('[data-i18n-html]').forEach((node) => { node.innerHTML = t(node.dataset.i18nHtml); });
    hydrateIcons();
  }


  function itemName(item) {
    return ({ "Mì gà": "Chicken noodles", "Cơm chiên": "Fried rice", "Trà sữa": "Milk tea", "Cơm sườn nướng": "Grilled pork rice", "Mì Ý": "Spaghetti", "Trà chanh": "Lemon tea", "Cơm gà": "Chicken rice", "Gỏi cuốn": "Fresh spring rolls", "Cơm rau củ": "Vegetable rice" })[item.name] || item.name;
  }

  function itemDescription(item) {
    return ({ "Mì nóng với thịt gà và rau": "Hot noodles with chicken and greens", "Cơm chiên trứng và rau củ": "Fried rice with egg and vegetables", "Trà sữa dùng lạnh": "Chilled milk tea", "Sườn nướng ăn kèm cơm": "Grilled pork served with rice", "Mì Ý sốt cà chua": "Spaghetti with tomato sauce", "Trà chanh mát lạnh": "Refreshing iced lemon tea", "Cơm gà cho bữa trưa": "Chicken rice for lunch", "Rau tươi cuốn bánh tráng": "Fresh vegetables in rice paper", "Cơm ăn kèm rau củ tươi": "Rice with fresh vegetables", "Cơm tấm sườn nướng": "Broken rice with grilled pork", "Cơm gà dùng kèm rau": "Chicken rice with greens" })[item.description] || item.description;
  }

  function categoryName(category) {
    if (category === "All") return t("all");
    if (category === "Món chính") return t("main_dish");
    if (category === "Món phụ") return t("side_dish");
    if (category === "Thức uống") return t("drink");
    return category;
  }

  async function loadHubs() {
    try {
      state.hubs = await api("/api/hubs");
      renderHubs();
    } catch (error) { $("#hub-count").textContent = t("load_error"); showNotice(error.message, "danger"); }
  }

  function renderHubs(filter = "") {
    const hubs = state.hubs.filter((hub) => `${hub.name} ${hub.address}`.toLowerCase().includes(filter.toLowerCase()));
    $("#hub-count").textContent = `${hubs.length} restaurants`;
    $("#hub-list").innerHTML = hubs.length ? hubs.map((hub) => `<article class="hub-card"><div class="hub-art ${escapeHtml(hub.icon || "restaurant")}" aria-hidden="true">${icon(hub.icon || "restaurant", "hub-icon")}</div><div class="hub-info"><span class="location-chip">${icon("map-pin")} ${t("on_campus")}</span><h2>${escapeHtml(hub.name)}</h2><a class="map-link" href="https://maps.google.com/?q=${encodeURIComponent(`${hub.name} ${hub.address}`)}" target="_blank" rel="noreferrer">${icon("map-pin")} ${escapeHtml(hub.address)}</a><div class="hub-meta">${icon("utensils")}<span>${escapeHtml(hub.description)}</span></div></div><button class="btn btn-outline-light hub-action" data-hub="${hub.id}"><span>${t("view_menu")}</span>${icon("arrow-right")}</button></article>`).join("") : `<div class="empty-state">${t("search_empty")}</div>`;
    $$("[data-hub]").forEach((button) => button.addEventListener("click", () => selectHub(Number(button.dataset.hub))));
  }

  async function selectHub(hubId) {
    const hub = state.hubs.find((item) => item.id === hubId);
    if (!hub) return;
    if (state.cartHubId && state.cartHubId !== hubId && cartCount()) {
      const confirmed = window.confirm(t("cancel_hub_change"));
      if (!confirmed) return;
      state.cart = {};
    }
    state.hub = hub;
    state.cartHubId = hubId;
    try {
      state.menu = await api(`/api/menu-items?hub_id=${hubId}`);
      $("#selected-hub-name").textContent = hub.name;
      $("#selected-hub-meta").innerHTML = `${icon(hub.icon || "restaurant")} ${escapeHtml(hub.address)} · ${t("menu_sample")}`;
      state.category = "All";
      renderCategories(); renderMenu(); toggleScreen("menu");
    } catch (error) { showNotice(error.message, "danger"); }
  }

  function renderCategories() {
    const categories = ["All", ...new Set(state.menu.map((item) => item.category).filter(Boolean))];
    $("#category-tabs").innerHTML = categories.map((category) => `<button class="${category === state.category ? "active" : ""}" data-category="${escapeHtml(category)}">${escapeHtml(categoryName(category))}</button>`).join("");
    $$("[data-category]").forEach((button) => button.addEventListener("click", () => { state.category = button.dataset.category; renderCategories(); renderMenu(); }));
  }

  function renderMenu() {
    const visible = state.menu.filter((item) => state.category === "All" || item.category === state.category);
    $("#menu-grid").innerHTML = visible.length ? visible.map((item, index) => `<article class="menu-card"><div class="food-art color-${index % 4}" aria-hidden="true">${icon("food", "food-icon")}</div><h2>${escapeHtml(itemName(item))}</h2><p>${escapeHtml(itemDescription(item) || "Freshly prepared for you")}</p><div class="menu-card-bottom"><span>${money(item.price)}</span><button class="btn btn-brand" data-add="${item.id}" ${item.is_available ? "" : "disabled"}>${icon("plus")} ${t("add")}</button></div></article>`).join("") : `<div class="empty-state">${t("no_menu")}</div>`;
    $$("[data-add]").forEach((button) => button.addEventListener("click", () => addToCart(Number(button.dataset.add))));
    updateCartBar();
  }

  function addToCart(itemId) {
    state.cart[itemId] = (state.cart[itemId] || 0) + 1;
    saveCart(); renderMenu();
  }
  function cartEntries() { return state.menu.filter((item) => state.cart[item.id]).map((item) => ({ ...item, quantity: state.cart[item.id] })); }
  function cartCount() { return Object.values(state.cart).reduce((sum, quantity) => sum + quantity, 0); }
  function subtotal() { return cartEntries().reduce((sum, item) => sum + item.price * item.quantity, 0); }
  function saveCart() {
    sessionStorage.setItem("saigonbite-cart", JSON.stringify(state.cart));
    if (state.cartHubId) sessionStorage.setItem("saigonbite-cart-hub", String(state.cartHubId));
    else sessionStorage.removeItem("saigonbite-cart-hub");
  }

  function updateCartBar() {
    const count = cartCount();
    $("#cart-count").textContent = `${count} ${count === 1 ? t("item") : t("items")}`;
    $("#cart-total").textContent = money(subtotal());
    $("#view-cart").disabled = !count;
  }

  function renderCart() {
    const entries = cartEntries();
    if (!entries.length) { toggleScreen("menu"); showNotice(t("empty_cart"), "info"); return; }
    $("#cart-hub").innerHTML = `<small>${t("placed_from")}</small><strong>${escapeHtml(state.hub?.name || "SaigonBite")}</strong>`;
    $("#cart-lines").innerHTML = entries.map((item) => `<article class="cart-line"><div class="cart-thumb">${icon("food")}</div><div><h3>${escapeHtml(itemName(item))}</h3><p>${money(item.price)}</p></div><div class="quantity-control"><button data-qty="${item.id}" data-delta="-1" aria-label="${"Decrease quantity"}">${icon("minus")}</button><span>${item.quantity}</span><button data-qty="${item.id}" data-delta="1" aria-label="${"Increase quantity"}">${icon("plus")}</button></div><button class="remove-item" data-remove="${item.id}" aria-label="${"Remove"} ${escapeHtml(itemName(item))}">${icon("close")}</button></article>`).join("");
    $("#cart-subtotal").textContent = money(subtotal());
    $("#cart-grand-total").textContent = money(subtotal());
    $$('[data-qty]').forEach((button) => button.addEventListener("click", () => changeQuantity(Number(button.dataset.qty), Number(button.dataset.delta))));
    $$('[data-remove]').forEach((button) => button.addEventListener("click", () => { delete state.cart[button.dataset.remove]; saveCart(); renderCart(); updateCartBar(); }));
    toggleScreen("cart");
  }

  function changeQuantity(itemId, delta) {
    state.cart[itemId] = (state.cart[itemId] || 0) + delta;
    if (state.cart[itemId] <= 0) delete state.cart[itemId];
    saveCart(); updateCartBar(); renderCart();
  }

  function renderCheckout() {
    if (!cartCount()) { showNotice(t("empty_cart_short"), "info"); toggleScreen("menu"); return; }
    $("#checkout-hub-name").textContent = state.hub?.name || "SaigonBite";
    $("#checkout-subtotal").textContent = money(subtotal());
    $("#checkout-total").textContent = money(subtotal());
    toggleScreen("checkout");
  }

  async function placeOrder(event) {
    event.preventDefault();
    clearNotice();
    if (!state.hub || !cartCount()) { showNotice(t("choose_items")); return; }
    const submit = $("#place-order");
    submit.disabled = true; submit.textContent = t("placing");
    try {
      const response = await api("/api/orders", { method: "POST", body: JSON.stringify({
        customer_id: 1,
        hub_id: state.hub.id,
        items: cartEntries().map((item) => ({ menu_item_id: item.id, quantity: item.quantity })),
        delivery_address: [
          $("#address").value.trim(),
          `Recipient: ${$("#recipient").value.trim()}`,
          `Phone: ${$("#phone").value.trim()}`,
          $("#note").value.trim() ? `Note: ${$("#note").value.trim()}` : ""
        ].filter(Boolean).join("\n"),
        delivery_distance_km: 0,
        payment_method: new FormData($("#checkout-form")).get("payment")
      }) });
      state.lastOrder = response;
      $("#success-order-id").textContent = `#SB${String(response.id).padStart(7, "0")}`;
      $("#success-hub").textContent = state.hub.name;
      $("#success-total").textContent = money(response.total);
      state.cart = {}; saveCart(); updateCartBar();
      toggleScreen("success");
    } catch (error) { showNotice(error.message, "danger"); }
    finally { submit.disabled = false; submit.innerHTML = `<span data-i18n="place_order">${t("place_order")}</span> ${icon("arrow-right")}`; }
  }

  const statusLabel = { PENDING: "Pending", CONFIRMED: "Confirmed", PREPARING: "Preparing", READY: "Ready for Pickup", DELIVERED: "Delivered", REJECTED: "Rejected", FAILED: "Delivery failed", CANCELLED: "Cancelled" };
  const orderCode = (id) => `#SB${String(id).padStart(7, "0")}`;
  const orderDate = (value) => new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
  const hubName = (id) => state.hubs.find((hub) => hub.id === id)?.name || `Hub ${id}`;
  const statusClass = (status) => String(status || "pending").toLowerCase();

  async function loadCustomerOrders() {
    const errorNode = $("#orders-error");
    errorNode.classList.add("d-none");
    try {
      // Current mock auth maps the signed-in customer to demo customer 1.
      state.customerOrders = await api("/api/customers/1/orders");
      renderCustomerOrders();
    } catch (error) {
      errorNode.textContent = `${error.message} Order history will appear when the customer order API is available.`;
      errorNode.classList.remove("d-none");
      $("#orders-table-body").innerHTML = "";
      $("#orders-empty").classList.remove("d-none");
    }
  }

  async function loadHome() {
    try {
      const [orders, hubs] = await Promise.all([api("/api/customers/1/orders"), api("/api/hubs")]);
      state.customerOrders = orders;
      state.hubs = hubs;
      $("#home-order-count").textContent = orders.length;
      $("#home-active-count").textContent = orders.filter((order) => ["PENDING", "CONFIRMED", "PREPARING", "READY"].includes(order.status)).length;
      $("#home-hub-count").textContent = hubs.length;
      const recent = orders.slice(0, 3);
      $("#home-recent-orders").innerHTML = recent.length ? recent.map((order) => `<button class="home-order-row" data-home-order="${order.id}"><span class="home-order-mark" data-icon="receipt"></span><span class="home-order-copy"><strong>${escapeHtml(hubName(order.hub_id))}</strong><small>${orderCode(order.id)} · ${orderDate(order.created_at)}</small></span><span class="order-status ${statusClass(order.status)}">${escapeHtml(statusLabel[order.status] || order.status)}</span><strong class="home-order-total">${money(order.total)}</strong><span class="home-action-arrow" data-icon="arrow-right"></span></button>`).join("") : `<div class="home-empty-card"><span class="home-empty-icon" data-icon="food"></span><strong>No orders yet</strong><p>When you place an order, you can follow every update here.</p><button class="btn btn-brand" data-open-view="order">Browse restaurants</button></div>`;
      $("#home-restaurants").innerHTML = hubs.slice(0, 3).map((hub) => `<button class="home-hub-card" data-home-hub="${hub.id}"><span class="home-hub-icon" data-icon="${escapeHtml(hub.icon || "restaurant")}"></span><span><strong>${escapeHtml(hub.name)}</strong><small>${escapeHtml(hub.description || "Nearby restaurant")}</small></span><span data-icon="arrow-right"></span></button>`).join("");
      hydrateIcons($("#view-home"));
      $$("[data-home-order]").forEach((button) => button.addEventListener("click", () => openOrder(Number(button.dataset.homeOrder), "detail")));
      $$("[data-home-hub]").forEach((button) => button.addEventListener("click", () => { showView("order"); selectHub(Number(button.dataset.homeHub)); }));
    } catch (error) {
      $("#home-recent-orders").innerHTML = `<div class="home-empty-card">${escapeHtml(error.message)}<p>Recent orders will appear here when the customer API is available.</p></div>`;
    }
  }

  function renderCustomerOrders(filter = "ALL") {
    const all = state.customerOrders || [];
    const visible = all.filter((order) => filter === "ALL" || (filter === "DELIVERING" ? ["CONFIRMED", "PREPARING", "READY"].includes(order.status) : filter === "COMPLETED" ? ["DELIVERED", "REJECTED", "FAILED", "CANCELLED"].includes(order.status) : order.status === filter));
    $("#order-count").textContent = `${visible.length} ${visible.length === 1 ? "order" : "orders"}`;
    $("#orders-empty").classList.toggle("d-none", visible.length > 0);
    $("#orders-table-body").innerHTML = visible.map((order) => `<tr><td><strong>${orderCode(order.id)}</strong></td><td>${escapeHtml(hubName(order.hub_id))}</td><td>${orderDate(order.created_at)}</td><td><strong>${money(order.total)}</strong></td><td><span class="order-status ${statusClass(order.status)}">${escapeHtml(statusLabel[order.status] || order.status)}</span></td><td><button class="btn btn-outline-brand btn-sm" data-order-detail="${order.id}">View details</button></td></tr>`).join("");
    const active = all.find((order) => ["PENDING", "CONFIRMED", "PREPARING", "READY"].includes(order.status));
    const featured = $("#featured-order");
    featured.classList.toggle("d-none", !active || filter !== "ALL");
    if (active && filter === "ALL") featured.innerHTML = `<div><span class="featured-kicker">${escapeHtml(statusLabel[active.status] || active.status)}</span><h2>${escapeHtml(hubName(active.hub_id))}</h2><p>${orderCode(active.id)} · ${money(active.total)}</p></div><div class="featured-total"><small>Current status</small><strong>${escapeHtml(statusLabel[active.status] || active.status)}</strong></div><button class="btn btn-brand" data-order-track="${active.id}">Track order ${icon("arrow-right")}</button>`;
    $$("[data-order-detail]").forEach((button) => button.addEventListener("click", () => openOrder(Number(button.dataset.orderDetail), "detail")));
    $$("[data-order-track]").forEach((button) => button.addEventListener("click", () => openOrder(Number(button.dataset.orderTrack), "track")));
  }

  async function openOrder(orderId, screen = "detail") {
    try {
      const order = await api(`/api/orders/${orderId}`);
      state.selectedOrder = order;
      renderOrderDetail(order);
      renderOrderTrack(order);
      renderOrderHistory(order);
      showOrdersScreen(screen);
    } catch (error) { showNotice(error.message, "danger"); }
  }

  function showOrdersScreen(screen) {
    showView("orders");
    ["list", "detail", "track", "history"].forEach((name) => {
      const elementId = name === "list" ? "orders-list-screen" : `order-${name}-screen`;
      $(`#${elementId}`).classList.toggle("d-none", name !== screen);
    });
    if (screen === "list") loadCustomerOrders();
  }
  function showView(name) {
    const views = { order: "view-order", orders: "view-orders", home: "view-home", vouchers: "view-vouchers", profile: "view-profile" };
    Object.entries(views).forEach(([key, id]) => $(`#${id}`).classList.toggle("d-none", key !== name));
    $$(".side-nav a").forEach((link) => link.classList.toggle("active", link.dataset.view === name));
  }
  function orderHeader(order, title) { return `<button class="text-back" data-orders-back>← &nbsp; My Orders</button><div class="order-title-row"><div><span class="eyebrow">${orderCode(order.id)}</span><h1>${title}</h1><p>${escapeHtml(hubName(order.hub_id))} · ${orderDate(order.created_at)}</p></div><span class="order-status ${statusClass(order.status)}">${escapeHtml(statusLabel[order.status] || order.status)}</span></div>`; }
  function orderItemsMarkup(order) { return (order.items || []).map((item) => `<div class="detail-item"><div><strong>${escapeHtml(item.name)}</strong><small>${item.quantity} × ${money(item.unit_price)}</small></div><strong>${money(item.line_total)}</strong></div>`).join(""); }
  function statusHistoryMarkup(order) {
    const history = order.status_history || [];
    return history.map((entry) => `<div class="timeline-entry"><span class="timeline-dot ${entry.status === order.status ? "current" : ""}"></span><div><strong>${escapeHtml(statusLabel[entry.status] || entry.status)}</strong>${entry.note ? `<p>${escapeHtml(entry.note)}</p>` : ""}</div><time>${new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit" }).format(new Date(entry.changed_at))}</time></div>`).join("") || `<p class="muted-copy">Status updates will appear here.</p>`;
  }
  function renderOrderDetail(order) {
    $("#order-detail-screen").innerHTML = `${orderHeader(order, "Order Details")}<div class="detail-layout"><div><section class="order-card"><div class="card-heading"><div><h2>${escapeHtml(hubName(order.hub_id))}</h2><p>${(order.items || []).length} items · Freshly made for you</p></div></div>${orderItemsMarkup(order)}</section><section class="order-card"><h2>Delivery information</h2><p>${escapeHtml(order.delivery_address || "Address not provided").replace(/\n/g, "<br>")}</p></section></div><aside class="summary-card"><h2>Order Summary</h2><div class="summary-row"><span>Payment method</span><strong>${escapeHtml(order.payment_method || "—")}</strong></div><div class="summary-row"><span>Payment status</span><strong>${escapeHtml(order.payment_status || "—")}</strong></div><div class="summary-row"><span>Subtotal</span><strong>${money(order.subtotal)}</strong></div><div class="summary-row"><span>Delivery fee</span><strong>${money(order.delivery_fee)}</strong></div><div class="summary-row"><span>Discount</span><strong>−${money(order.discount)}</strong></div><div class="summary-row total-row"><span>Total</span><strong>${money(order.total)}</strong></div><button class="btn btn-brand w-100 mt-3" data-open-track="${order.id}">Track order ${icon("arrow-right")}</button><button class="btn btn-outline-brand w-100 mt-2" data-open-history="${order.id}">View status history</button></aside></div>`;
    bindOrderNavigation("detail");
  }
  function renderOrderTrack(order) {
    const steps = ["PENDING", "CONFIRMED", "PREPARING", "READY", "DELIVERED"];
    const terminal = ["REJECTED", "FAILED", "CANCELLED"].includes(order.status);
    const activeIndex = steps.indexOf(order.status);
    $("#order-track-screen").innerHTML = `${orderHeader(order, "Track Current Order")}<section class="eta-card"><div><small>Estimated delivery</small><strong>${terminal ? "Update unavailable" : "We'll update you as your order progresses"}</strong></div><button class="btn btn-outline-brand" data-open-history="${order.id}">View status history →</button></section><section class="order-card"><h2>From our kitchen to your doorstep</h2><div class="progress-steps ${terminal ? "terminal" : ""}">${steps.map((step, index) => `<div class="progress-step ${index <= activeIndex && !terminal ? "done" : ""} ${step === order.status ? "active" : ""}"><span>${index < activeIndex && !terminal ? "✓" : index + 1}</span><strong>${escapeHtml(statusLabel[step])}</strong></div>`).join("")}</div></section><div class="detail-layout"><section class="order-card"><h2>Your order hub</h2><strong>${escapeHtml(hubName(order.hub_id))}</strong><p>${escapeHtml(order.delivery_address || "")}</p><button class="text-back" data-open-detail="${order.id}">View order details →</button></section><section class="order-card"><h2>Latest updates</h2>${statusHistoryMarkup(order)}</section></div>`;
    bindOrderNavigation("track");
  }
  function renderOrderHistory(order) {
    $("#order-history-screen").innerHTML = `${orderHeader(order, "Order Status History")}<div class="detail-layout"><section class="order-card"><h2>Every step of your order</h2><p class="muted-copy">A complete record of updates, from first to latest.</p><div class="timeline">${statusHistoryMarkup(order)}</div></section><aside class="summary-card"><h2>Order at a glance</h2><p><strong>${orderCode(order.id)}</strong></p><hr><small>Hub</small><p><strong>${escapeHtml(hubName(order.hub_id))}</strong></p><small>Current status</small><p><span class="order-status ${statusClass(order.status)}">${escapeHtml(statusLabel[order.status] || order.status)}</span></p><button class="btn btn-brand w-100" data-open-track="${order.id}">Track order ${icon("arrow-right")}</button><button class="btn btn-outline-brand w-100 mt-2" data-open-detail="${order.id}">View order details</button></aside></div>`;
    bindOrderNavigation("history");
  }
  function bindOrderNavigation(screen) {
    const root = $(`#order-${screen}-screen`);
    root.querySelectorAll('[data-orders-back]').forEach((button) => button.addEventListener("click", () => showOrdersScreen("list")));
    root.querySelectorAll('[data-open-track]').forEach((button) => button.addEventListener("click", () => showOrdersScreen("track")));
    root.querySelectorAll('[data-open-history]').forEach((button) => button.addEventListener("click", () => showOrdersScreen("history")));
    root.querySelectorAll('[data-open-detail]').forEach((button) => button.addEventListener("click", () => showOrdersScreen("detail")));
  }

  async function initialize() {
    try {
      const user = await api("/api/auth/me", { headers: { "Content-Type": "application/json" } });
      if (user.role !== "CUSTOMER") { location.assign(user.redirect_url); return; }
      state.user = user;
      const displayName = user.email.split("@")[0].replace(/[._-]/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
      $("#customer-name").textContent = displayName;
      $("#home-customer-name").textContent = displayName;
      $("#profile-customer-name").textContent = displayName;
      $("#profile-name-field").textContent = displayName;
      $("#profile-customer-email").textContent = user.email;
      $("#profile-email-field").textContent = user.email;
    } catch { return; }
    applyLanguage();
    await loadHubs();
    await loadHome();
    $("#hub-search").addEventListener("input", (event) => renderHubs(event.target.value));
    $$("[data-order-filter]").forEach((button) => button.addEventListener("click", () => { $$("[data-order-filter]").forEach((item) => item.classList.toggle("active", item === button)); renderCustomerOrders(button.dataset.orderFilter); }));
    $("#back-hubs").addEventListener("click", () => toggleScreen("hub"));
    $("#back-menu").addEventListener("click", () => toggleScreen("menu"));
    $("#back-cart").addEventListener("click", renderCart);
    $("#view-cart").addEventListener("click", renderCart);
    $("#proceed-checkout").addEventListener("click", renderCheckout);
    $("#checkout-form").addEventListener("submit", placeOrder);
    $("#apply-voucher").addEventListener("click", () => showNotice(t("demo_error"), "info"));
    $("#track-order").addEventListener("click", () => state.lastOrder && openOrder(state.lastOrder.id, "track"));
    $("#order-again").addEventListener("click", () => { toggleScreen("hub"); renderHubs(); });
    $("#logout").addEventListener("click", logout);
    $$('[data-logout]').forEach((button) => button.addEventListener("click", logout));
    document.addEventListener("click", (event) => {
      const action = event.target.closest("[data-open-view]");
      if (!action) return;
      const target = action.dataset.openView;
      showView(target);
      if (target === "orders") showOrdersScreen("list");
      if (target === "home") loadHome();
    });
    $$(".side-nav a").forEach((link) => link.addEventListener("click", (event) => {
      event.preventDefault(); $$(".side-nav a").forEach((item) => item.classList.toggle("active", item === link));
      const target = link.dataset.view;
      showView(target);
      if (target === "orders") showOrdersScreen("list");
      if (target === "home") loadHome();
    }));
    hydrateIcons();
  }

  async function logout() {
    const buttons = $$('[data-logout], #logout');
    buttons.forEach((button) => { button.disabled = true; });
    try { await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" }); }
    finally { location.assign("/"); }
  }

  initialize();
})();
