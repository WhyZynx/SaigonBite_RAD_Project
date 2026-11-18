(() => {
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const money = (amount) => new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(amount || 0);
  const MOCK_DELIVERY_DISTANCE_KM = 3.5;
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
    food: '<path d="M3 11h18a9 9 0 0 1-18 0zM5 7a8 8 0 0 1 14 0M12 3v2"/>',
    cart: '<path d="M3 4h2l2.2 11.2a2 2 0 0 0 2 1.6h7.9a2 2 0 0 0 1.9-1.4L21 9H6"/><circle cx="10" cy="20" r="1"/><circle cx="18" cy="20" r="1"/>'
  };
  function icon(name, className = "icon") { return `<svg class="${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.food}</svg>`; }
  function hydrateIcons(root = document) { root.querySelectorAll("[data-icon]").forEach((node) => { node.innerHTML = icon(node.dataset.icon, "icon"); }); }
  const copy = {
    en: {
      tagline:"GOOD FOOD, CLOSE BY",home:"Home",order_food:"Order Food",my_orders:"My Orders",vouchers:"Vouchers",profile:"Profile",footer_tagline:"Freshly made.\nHappily delivered.",hello:"Hello,",customer_account:"Customer account",logout:"Log out",nearby_label:"NEARBY RESTAURANTS",hero_title:"What are you craving today?",hero_subtitle:"Choose a nearby restaurant and explore its menu.",search_placeholder:"Search restaurants...",search_hint:"Search by name or location",restaurants:"NEARBY RESTAURANTS",menu_demo_note:"Sample menu and prices for this demo. They may differ from the restaurant's current menu.",your_cart:"Your Cart",view_cart:"View cart",cart_subtitle:"Review your items before placing the order.",order_summary:"Order Summary",subtotal:"Subtotal",total:"Total",delivery_fee_not_included:"Delivery fee is not included.",continue_checkout:"Continue to Checkout",checkout_title:"Checkout",checkout_subtitle:"A few details and your restaurant will get cooking.",delivery_information:"Delivery Information",delivery_address:"Delivery address",address_placeholder:"Street, building, apartment...",recipient_name:"Recipient name",name_placeholder:"Your name",phone_number:"Phone number",note_optional:"Note (optional)",note_placeholder:"For example: call when you arrive",voucher:"Voucher",voucher_placeholder:"Enter voucher code",apply:"Apply",voucher_unavailable:"Voucher validation is not connected yet.",payment_method:"Payment Method",cod:"Cash on Delivery (COD)",delivery_fee:"Delivery fee",not_calculated:"Not calculated",discount:"Discount",delivery_fee_note:"Delivery fee is not included in this demo.",place_order:"Place Order",order_success_eyebrow:"ORDER PLACED SUCCESSFULLY",order_success_title:"Your order is on its way!",order_number:"Order number",order_success_message:"The restaurant will confirm and prepare your order.",restaurant:"Restaurant",order_total:"Order total",status:"Status",order_status_message:"Your order status will update when the restaurant confirms.",order_again:"Order Again",track_order:"Track Order",placeholder_prompt:"Choose",placeholder_suffix:"to browse nearby restaurants.",search_empty:"No restaurants match your search.",view_menu:"View menu",on_campus:"Nearby restaurant",menu_sample:"Sample menu",add:"Add",all:"All",items:"items",item:"item",placed_from:"ORDER FROM",empty_cart:"Your cart is empty. Add a dish to continue.",empty_cart_short:"Your cart is empty.",demo_error:"This feature is not connected yet.",cancel_hub_change:"Changing restaurants will clear the current cart. Continue?",choose_items:"Choose a restaurant and add at least one item.",placing:"Placing order...",track_pending:"Order {id} is PENDING. Order tracking is part of UC02.",load_error:"Unable to load restaurants",no_menu:"No sample menu is available for this restaurant.",main_dish:"Main dish",side_dish:"Side dish",drink:"Drinks"
    }
  };
  let language = "en";
  const t = (key) => copy[language][key] || copy.en[key] || key;
  const state = { hubs: [], hub: null, menu: [], category: "All", cart: {}, cartCatalog: {}, cartHubId: Number(sessionStorage.getItem("saigonbite-cart-hub")) || null, lastOrder: null, screen: "hub", user: null, customerOrders: [] };
  const savedCart = sessionStorage.getItem("saigonbite-cart");
  if (savedCart) {
    try { Object.assign(state.cart, JSON.parse(savedCart)); } catch { sessionStorage.removeItem("saigonbite-cart"); }
  }
  const savedCartCatalog = sessionStorage.getItem("saigonbite-cart-catalog");
  if (savedCartCatalog) {
    try { Object.assign(state.cartCatalog, JSON.parse(savedCartCatalog)); } catch { sessionStorage.removeItem("saigonbite-cart-catalog"); }
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
    ["hub", "menu", "cart", "restaurant-cart", "checkout", "success"].forEach((screen) => $(`#${screen}-screen`)?.classList.toggle("d-none", screen !== name));
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

  const menuImage = {
    "Com Tam Suon Bi Cha": "suon_bi_cha.jpeg",
    "Pho Bo Tai Nam": "pho_tai_nam.jpeg",
    "Tra Dao Cam Sa": "tradaocamsa.jpeg",
    "Com Ga Xoi Mo": "com_ga_xoi_mo.jpeg",
    "Bun Bo Hue Dac Bien": "bun_bo_hue.jpeg",
    "Banh Mi Thit Nuong": "banhmi_thit_nuong.jpeg",
    "Com Tam Suon Trung": "suon_trung.jpeg",
    "Tra Sua Tran Chau Duong Den": "tran_chau_duong_den.jpeg"
  };
  function foodImage(item, className = "food-thumb-image") {
    const filename = menuImage[item.name];
    return filename
      ? `<img class="${className}" src="/img/${filename}" alt="${escapeHtml(item.name)}" loading="lazy">`
      : icon("food", "food-icon");
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
    $("#hub-list").innerHTML = hubs.length ? hubs.map((hub) => `<article class="hub-card"><div class="hub-art ${escapeHtml(hub.icon || "restaurant")}" aria-hidden="true">${icon(hub.icon || "restaurant", "hub-icon")}</div><div class="hub-info"><span class="location-chip">${icon("map-pin")} ${t("on_campus")}</span><h2>${escapeHtml(hub.name)}</h2><a class="map-link" href="https://maps.google.com/?q=${encodeURIComponent(`${hub.name} ${hub.address}`)}" target="_blank" rel="noreferrer">${icon("map-pin")} ${escapeHtml(hub.address)}</a>${hub.description ? `<div class="hub-meta">${icon("utensils")}<span>${escapeHtml(hub.description)}</span></div>` : ""}</div><button class="btn btn-outline-light hub-action" data-hub="${hub.id}"><span>${t("view_menu")}</span>${icon("arrow-right")}</button></article>`).join("") : `<div class="empty-state">${t("search_empty")}</div>`;
    $$("[data-hub]").forEach((button) => button.addEventListener("click", () => selectHub(Number(button.dataset.hub))));
  }

  async function selectHub(hubId) {
    const hub = state.hubs.find((item) => item.id === hubId);
    if (!hub) return;
    state.hub = hub;
    try {
      state.menu = await api(`/api/menu-items?hub_id=${hubId}`);
      state.menu.forEach((item) => {
        if (state.cart[item.id]) state.cartCatalog[item.id] = { ...item, hub_id: hubId, hub_name: hub.name };
      });
      saveCart();
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
    $("#menu-grid").innerHTML = visible.length ? visible.map((item, index) => {
      const image = menuImage[item.name];
      const visual = image
        ? `<img class="food-photo" src="/img/${image}" alt="${escapeHtml(item.name)}" loading="lazy">`
        : icon("food", "food-icon");
      return `<article class="menu-card"><div class="food-art color-${index % 4}">${visual}</div><h2>${escapeHtml(itemName(item))}</h2><p>${escapeHtml(itemDescription(item) || "Freshly prepared for you")}</p><div class="menu-card-bottom"><span>${money(item.price)}</span><button class="btn btn-brand" data-add="${item.id}" ${item.is_available ? "" : "disabled"}>${icon("plus")} ${t("add")}</button></div></article>`;
    }).join("") : `<div class="empty-state">${t("no_menu")}</div>`;
    $$("[data-add]").forEach((button) => button.addEventListener("click", () => addToCart(Number(button.dataset.add))));
    updateCartBar();
  }

  function addToCart(itemId) {
    const item = state.menu.find((entry) => entry.id === itemId);
    if (!item || !state.hub) return;
    state.cart[itemId] = (state.cart[itemId] || 0) + 1;
    state.cartCatalog[itemId] = { ...item, hub_id: state.hub.id, hub_name: state.hub.name };
    saveCart(); renderMenu();
  }
  function cartEntries() { return Object.entries(state.cart).filter(([, quantity]) => quantity > 0).map(([id, quantity]) => ({ ...state.cartCatalog[id], id: Number(id), quantity })).filter((item) => item.name); }
  function cartGroups() {
    const groups = new Map();
    cartEntries().forEach((item) => {
      const hubId = item.hub_id;
      if (!groups.has(hubId)) groups.set(hubId, { hub_id: hubId, hub_name: item.hub_name || hubName(hubId), items: [] });
      groups.get(hubId).items.push(item);
    });
    return [...groups.values()];
  }
  function cartCount() { return Object.values(state.cart).reduce((sum, quantity) => sum + quantity, 0); }
  function subtotal() { return cartEntries().reduce((sum, item) => sum + item.price * item.quantity, 0); }
  function saveCart() {
    sessionStorage.setItem("saigonbite-cart", JSON.stringify(state.cart));
    sessionStorage.setItem("saigonbite-cart-catalog", JSON.stringify(state.cartCatalog));
    sessionStorage.removeItem("saigonbite-cart-hub");
  }

  function updateCartBar() {
    const allCount = cartCount();
    const restaurantItems = state.hub ? cartEntries().filter((item) => item.hub_id === state.hub.id) : [];
    const restaurantCount = restaurantItems.reduce((sum, item) => sum + item.quantity, 0);
    const restaurantSubtotal = restaurantItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
    $("#cart-count").textContent = `${restaurantCount} ${restaurantCount === 1 ? t("item") : t("items")}`;
    $("#cart-total").textContent = money(restaurantSubtotal);
    $("#global-cart-count").textContent = String(allCount);
    $("#global-cart").disabled = false;
    $("#view-cart").disabled = allCount === 0;
  }

  function renderCart() {
    const groups = cartGroups();
    if (!groups.length) {
      $("#cart-restaurants").innerHTML = `<div class="empty-state">${t("empty_cart_short")}</div>`;
      toggleScreen("cart");
      return;
    }
    $("#cart-restaurants").innerHTML = groups.map((group) => {
      const count = group.items.reduce((sum, item) => sum + item.quantity, 0);
      const groupSubtotal = group.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
      return `<button class="cart-restaurant-card" type="button" data-cart-hub="${group.hub_id}"><span class="cart-restaurant-photo">${foodImage(group.items[0])}</span><span class="cart-restaurant-copy"><strong>${escapeHtml(group.hub_name)}</strong><small>${count} ${count === 1 ? t("item") : t("items")} · ${money(groupSubtotal)}</small></span>${icon("arrow-right")}</button>`;
    }).join("");
    $$('[data-cart-hub]').forEach((button) => button.addEventListener("click", () => renderRestaurantCart(Number(button.dataset.cartHub))));
    toggleScreen("cart");
  }

  function renderRestaurantCart(hubId) {
    const group = cartGroups().find((item) => item.hub_id === hubId);
    if (!group) { renderCart(); return; }
    state.selectedCartHubId = hubId;
    state.hub = state.hubs.find((hub) => hub.id === hubId) || state.hub;
    $("#restaurant-cart-title").textContent = group.hub_name;
    $("#cart-hub").innerHTML = `<small>${t("placed_from")}</small><strong>${escapeHtml(group.hub_name)}</strong>`;
    $("#cart-lines").innerHTML = group.items.map((item) => `<article class="cart-line"><div class="cart-thumb">${foodImage(item)}</div><div><h3>${escapeHtml(itemName(item))}</h3><p>${money(item.price)}</p></div><div class="quantity-control"><button data-qty="${item.id}" data-delta="-1" aria-label="Decrease quantity">${icon("minus")}</button><span>${item.quantity}</span><button data-qty="${item.id}" data-delta="1" aria-label="Increase quantity">${icon("plus")}</button></div><button class="remove-item" data-remove="${item.id}" aria-label="Remove ${escapeHtml(itemName(item))}">${icon("close")}</button></article>`).join("");
    const restaurantSubtotal = group.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    $("#cart-subtotal").textContent = money(restaurantSubtotal);
    $("#cart-grand-total").textContent = money(restaurantSubtotal);
    $$('[data-qty]').forEach((button) => button.addEventListener("click", () => changeQuantity(Number(button.dataset.qty), Number(button.dataset.delta))));
    $$('[data-remove]').forEach((button) => button.addEventListener("click", () => { delete state.cart[button.dataset.remove]; delete state.cartCatalog[button.dataset.remove]; saveCart(); updateCartBar(); renderRestaurantCart(hubId); }));
    toggleScreen("restaurant-cart");
  }

  function changeQuantity(itemId, delta) {
    state.cart[itemId] = (state.cart[itemId] || 0) + delta;
    if (state.cart[itemId] <= 0) { delete state.cart[itemId]; delete state.cartCatalog[itemId]; }
    saveCart(); updateCartBar();
    if (state.screen === "restaurant-cart" && state.selectedCartHubId) renderRestaurantCart(state.selectedCartHubId);
    else renderCart();
  }

  function renderCheckout() {
    const group = cartGroups().find((item) => item.hub_id === state.selectedCartHubId);
    if (!group) { renderCart(); showNotice(t("empty_cart_short"), "info"); return; }
    const groupSubtotal = group.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    $("#checkout-hub-name").textContent = group.hub_name;
    $("#checkout-subtotal").textContent = money(groupSubtotal);
    updateCheckoutTotals();
    toggleScreen("checkout");
  }

  function updateCheckoutTotals() {
    const fee = 15000;
    $("#checkout-delivery-fee").textContent = money(fee);
    const groupSubtotal = cartGroups().find((group) => group.hub_id === state.selectedCartHubId)?.items.reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;
    $("#checkout-total").textContent = money(groupSubtotal + fee);
  }

  async function placeOrder(event) {
    event.preventDefault();
    clearNotice();
    const group = cartGroups().find((item) => item.hub_id === state.selectedCartHubId);
    if (!group) { showNotice(t("choose_items")); return; }
    const submit = $("#place-order");
    submit.disabled = true; submit.textContent = t("placing");
    try {
      const address = [
        $("#address").value.trim(),
        `Recipient: ${$("#recipient").value.trim()}`,
        `Phone: ${$("#phone").value.trim()}`,
        $("#note").value.trim() ? `Note: ${$("#note").value.trim()}` : ""
      ].filter(Boolean).join("\n");
      const response = await api("/api/orders", { method: "POST", body: JSON.stringify({
        customer_id: 1,
        hub_id: group.hub_id,
        items: group.items.map((item) => ({ menu_item_id: item.id, quantity: item.quantity })),
        delivery_address: address,
        delivery_distance_km: MOCK_DELIVERY_DISTANCE_KM,
        payment_method: "COD"
      }) });
      state.lastOrder = response;
      $("#success-order-id").textContent = `#SB${String(response.id).padStart(7, "0")}`;
      $("#success-hub").textContent = group.hub_name;
      $("#success-total").textContent = money(response.total);
      group.items.forEach((item) => { delete state.cart[item.id]; delete state.cartCatalog[item.id]; });
      saveCart(); updateCartBar();
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
    $("#customer-footer").classList.toggle("d-none", !["order", "home"].includes(name));
    $$(".side-nav a").forEach((link) => link.classList.toggle("active", link.dataset.view === name));
  }
  function orderHeader(order, title) { return `<button class="text-back" data-orders-back>← &nbsp; My Orders</button><div class="order-title-row"><div><span class="eyebrow">${orderCode(order.id)}</span><h1>${title}</h1><p>${escapeHtml(hubName(order.hub_id))} · ${orderDate(order.created_at)}</p></div><span class="order-status ${statusClass(order.status)}">${escapeHtml(statusLabel[order.status] || order.status)}</span></div>`; }
  function orderItemsMarkup(order) { return (order.items || []).map((item) => `<div class="detail-item"><span class="detail-thumb">${foodImage(item)}</span><div><strong>${escapeHtml(item.name)}</strong><small>${item.quantity} × ${money(item.unit_price)}</small></div><strong>${money(item.line_total)}</strong></div>`).join(""); }
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
    if (cartCount() && !Object.keys(state.cartCatalog).length && state.cartHubId) {
      const oldHub = state.hubs.find((hub) => hub.id === state.cartHubId);
      if (oldHub) {
        const oldMenu = await api(`/api/menu-items?hub_id=${oldHub.id}`).catch(() => []);
        oldMenu.forEach((item) => {
          if (state.cart[item.id]) state.cartCatalog[item.id] = { ...item, hub_id: oldHub.id, hub_name: oldHub.name };
        });
      }
    }
    if (cartCount()) {
      const hubIds = new Set(Object.values(state.cartCatalog).map((item) => item.hub_id));
      for (const hubId of hubIds) {
        const hub = state.hubs.find((item) => item.id === hubId);
        const freshMenu = hub ? await api(`/api/menu-items?hub_id=${hubId}`).catch(() => []) : [];
        Object.keys(state.cart).forEach((id) => {
          const stored = state.cartCatalog[id];
          if (!stored) { delete state.cart[id]; return; }
          if (stored.hub_id !== hubId) return;
          const fresh = freshMenu.find((item) => item.id === Number(id));
          if (fresh) state.cartCatalog[id] = { ...fresh, hub_id: hubId, hub_name: hub.name };
          else { delete state.cart[id]; delete state.cartCatalog[id]; }
        });
      }
      Object.keys(state.cart).forEach((id) => { if (!state.cartCatalog[id]) delete state.cart[id]; });
      saveCart();
    }
    updateCartBar();
    await loadHome();
    $("#hub-search").addEventListener("input", (event) => renderHubs(event.target.value));
    $$("[data-order-filter]").forEach((button) => button.addEventListener("click", () => { $$("[data-order-filter]").forEach((item) => item.classList.toggle("active", item === button)); renderCustomerOrders(button.dataset.orderFilter); }));
    $("#back-hubs").addEventListener("click", () => toggleScreen("hub"));
    $("#back-menu").addEventListener("click", () => { showView("order"); toggleScreen("hub"); });
    $("#back-all-carts").addEventListener("click", renderCart);
    $("#back-cart").addEventListener("click", () => renderRestaurantCart(state.selectedCartHubId));
    $("#view-cart").addEventListener("click", () => {
      if (state.hub) renderRestaurantCart(state.hub.id);
      else renderCart();
    });
    $("#global-cart").addEventListener("click", () => { showView("order"); renderCart(); });
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
