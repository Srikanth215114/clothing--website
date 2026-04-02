/* ============================================================
   lit-up | script.js — nav + API-backed cart, auth, storefront
   Set window.LITUP_API_BASE = 'https://your-api.com' when frontend is on GitHub Pages.
   ============================================================ */

let LITUP_PRODUCTS = {
  1: { id: 1, name: 'satoru gojo', img: './images/products/product-1.webp', price: 799 },
  2: { id: 2, name: 'monkey d luffy', img: './images/products/product-2.webp', price: 799 },
  3: { id: 3, name: 'vegeta ultra ego', img: './images/products/product-3.webp', price: 799 },
  4: { id: 4, name: 'naruto uzumaki', img: './images/products/product-4.webp', price: 799 },
  5: { id: 5, name: 'kakashi hatake', img: './images/products/product-5.webp', price: 799 },
  6: { id: 6, name: 'gojo satoru', img: './images/products/product-6.webp', price: 799 },
  7: { id: 7, name: 'kakarot', img: './images/products/product-7.webp', price: 799 },
  8: { id: 8, name: 'son goku', img: './images/products/product-8.webp', price: 799 },
  9: { id: 9, name: 'master roshi', img: './images/products/product-9.webp', price: 799 },
  10: { id: 10, name: 'itachi uchiha', img: './images/products/product-10.webp', price: 799 },
  11: { id: 11, name: 'meliodas', img: './images/products/product-11.webp', price: 799 },
  12: { id: 12, name: 'vegeta', img: './images/products/product-12.webp', price: 799 },
  13: { id: 13, name: 'sukuna', img: './images/products/product-13.webp', price: 799 },
  14: { id: 14, name: 'zenitsu', img: './images/products/product-14.webp', price: 799 },
  15: { id: 15, name: 'sung jin woo', img: './images/products/product-15.webp', price: 799 },
  16: { id: 16, name: 'satoru gojo black', img: './images/products/product-16.webp', price: 799 }
};

window.LITUP_PRODUCTS = LITUP_PRODUCTS;

function getApiBase() {
  if (typeof window.LITUP_API_BASE === 'string' && window.LITUP_API_BASE.trim()) {
    return window.LITUP_API_BASE.replace(/\/$/, '');
  }
  return '';
}

/**
 * @param {string} path - e.g. '/api/products'
 * @param {RequestInit} options
 */
async function apiFetch(path, options = {}) {
  const base = getApiBase();
  const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
  const headers = new Headers(options.headers || {});
  const token = Store.getToken();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Content-Type') && options.body && typeof options.body === 'string') {
    headers.set('Content-Type', 'application/json');
  }
  const res = await fetch(url, { ...options, headers, credentials: 'include' });
  let body = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  if (!res.ok) {
    const msg = body && body.error && body.error.message ? body.error.message : res.statusText || 'Request failed';
    const err = new Error(msg);
    err.status = res.status;
    err.body = body;
    throw err;
  }
  return body;
}

const Store = {
  TOKEN_KEY: 'litup_access_token',
  USER_KEY: 'litup_user',

  getToken: () => localStorage.getItem(Store.TOKEN_KEY),
  setToken: (t) => {
    if (t) localStorage.setItem(Store.TOKEN_KEY, t);
    else localStorage.removeItem(Store.TOKEN_KEY);
  },
  getUser: () => {
    try {
      return JSON.parse(localStorage.getItem(Store.USER_KEY) || 'null');
    } catch {
      return null;
    }
  },
  setUser: (u) => {
    if (u) localStorage.setItem(Store.USER_KEY, JSON.stringify(u));
    else localStorage.removeItem(Store.USER_KEY);
  },
  clearSession: () => {
    Store.setToken(null);
    Store.setUser(null);
    try {
      localStorage.removeItem('litup_cart');
      localStorage.removeItem('litup_users');
    } catch { /* ignore */ }
  }
};

function normalizeProductName(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function findProductByName(name) {
  const normalized = normalizeProductName(name);
  return Object.values(LITUP_PRODUCTS).find(
    product => normalizeProductName(product.name) === normalized
  ) || null;
}

function setActiveAuthView(view) {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const logBtn = document.getElementById('removeLog');
  const regBtn = document.getElementById('removeReg');
  if (!loginForm || !registerForm || !logBtn || !regBtn) return;

  const isLogin = view !== 'register';
  loginForm.classList.toggle('active', isLogin);
  registerForm.classList.toggle('active', !isLogin);
  loginForm.toggleAttribute('hidden', !isLogin);
  registerForm.toggleAttribute('hidden', isLogin);
  logBtn.setAttribute('aria-pressed', String(isLogin));
  regBtn.setAttribute('aria-pressed', String(!isLogin));
}

window.login = () => setActiveAuthView('login');
window.register = () => setActiveAuthView('register');

/* ---------- Mobile Nav Toggle ---------- */
const toggle = document.querySelector('.toggle');
const navMenu = document.querySelector('.nav-menu');
if (toggle && navMenu) {
  if (!navMenu.id) navMenu.id = 'site-navigation';
  toggle.setAttribute('aria-controls', navMenu.id);
  toggle.setAttribute('aria-expanded', 'false');

  const closeMenu = () => {
    navMenu.classList.remove('active');
    toggle.setAttribute('aria-expanded', 'false');
  };

  const openMenu = () => {
    navMenu.classList.add('active');
    toggle.setAttribute('aria-expanded', 'true');
  };

  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    if (expanded) closeMenu();
    else openMenu();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeMenu();
  });

  navMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeMenu);
  });
}

/* ---------- Swiper (home page) ---------- */
(function initHomeSwiper() {
  const homeSwiper = document.querySelector('.home__swiper');
  if (!homeSwiper || typeof Swiper === 'undefined' || homeSwiper.dataset.swiperReady === 'true') return;

  const prevButton = document.querySelector('.swiper-button-prev');
  const nextButton = document.querySelector('.swiper-button-next');
  if (prevButton) prevButton.setAttribute('aria-label', 'Show previous featured product');
  if (nextButton) nextButton.setAttribute('aria-label', 'Show next featured product');

  new Swiper('.home__swiper', {
    loop: true,
    loopAdditionalSlides: 2,
    grabCursor: true,
    slidesPerView: 3,
    centeredSlides: true,
    spaceBetween: 24,
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev'
    },
    keyboard: { enabled: true },
    breakpoints: {
      0: { slidesPerView: 1, spaceBetween: 0 },
      600: { slidesPerView: 3, spaceBetween: 24 }
    }
  });

  homeSwiper.dataset.swiperReady = 'true';
})();

/* ---------- Cart badge ---------- */
async function updateCartBadge() {
  const cartIcon = document.querySelector('a[href*="cart"] img.cart');
  if (!cartIcon) return;

  let badge = document.querySelector('.cart-badge');
  if (!badge) {
    badge = document.createElement('span');
    badge.className = 'cart-badge';
    badge.setAttribute('aria-hidden', 'true');
    cartIcon.parentElement.style.position = 'relative';
    cartIcon.parentElement.appendChild(badge);
  }

  const token = Store.getToken();
  if (!token) {
    badge.textContent = '0';
    badge.style.display = 'none';
    cartIcon.parentElement.setAttribute('aria-label', 'Shopping cart');
    return;
  }

  try {
    const json = await apiFetch('/api/cart', { method: 'GET' });
    const items = (json.data && json.data.items) || [];
    const total = items.reduce((sum, item) => sum + (item.quantity || 0), 0);
    cartIcon.parentElement.setAttribute(
      'aria-label',
      `Shopping cart with ${total} item${total === 1 ? '' : 's'}`
    );
    badge.textContent = total;
    badge.style.display = total ? 'flex' : 'none';
  } catch {
    badge.style.display = 'none';
  }
}

updateCartBadge();

/* ---------- Optional: hydrate catalog from API (keeps IDs in sync with DB) ---------- */
(async function hydrateProductsFromApi() {
  try {
    const json = await apiFetch('/api/products', { method: 'GET' });
    const list = json.data || [];
    if (!Array.isArray(list) || !list.length) return;
    const map = {};
    list.forEach(p => {
      const rupees = typeof p.price === 'number' ? p.price : (p.price_cents || 0) / 100;
      map[p.id] = {
        id: p.id,
        name: p.name,
        img: p.image_url || '',
        price: Math.round(rupees)
      };
    });
    LITUP_PRODUCTS = map;
    window.LITUP_PRODUCTS = map;
    // Re-run product detail loader now that live data is available
    if (typeof window.__reloadProductDetail === 'function') window.__reloadProductDetail();
  } catch {
    /* offline or API down — keep bundled LITUP_PRODUCTS */
  }
})();

/* ============================================================
   ADD TO CART (Flask API)
   ============================================================ */
async function addToCart(id, name, price, img, size, qty) {
  if (!Store.getToken()) {
    showToast('Please log in to add items to your cart.', 'error');
    setTimeout(() => {
      window.location.href = './account.html';
    }, 1200);
    return;
  }

  const safeQty = Math.max(1, parseInt(qty, 10) || 1);
  const safeSize = (size && String(size).trim()) || 'M';

  try {
    await apiFetch('/api/cart/add', {
      method: 'POST',
      body: JSON.stringify({
        product_id: parseInt(id, 10),
        quantity: safeQty,
        size: safeSize
      })
    });
    await updateCartBadge();
    showToast(`${name} added to cart.`, 'success');
  } catch (e) {
    showToast(e.message || 'Could not add to cart.', 'error');
  }
}

window.addToCart = addToCart;

(function initProductPage() {
  const addBtn = document.querySelector('.add-to-cart-btn');
  if (!addBtn) return;

  if (document.getElementById('sizeSelector')) return;

  addBtn.addEventListener('click', () => {
    const sizeEl = document.querySelector('select[name="size"]');
    const qtyEl = document.querySelector('input[type="number"]');
    const size = sizeEl ? sizeEl.value : 'M';

    if (!sizeEl || !sizeEl.value || sizeEl.value === 'Select Size') {
      showToast('Please select a size.', 'error');
      return;
    }

    const qty = qtyEl ? parseInt(qtyEl.value, 10) || 1 : 1;
    void addToCart(
      addBtn.dataset.id,
      addBtn.dataset.name,
      parseInt(addBtn.dataset.price, 10),
      addBtn.dataset.img,
      size,
      qty
    );
  });
})();

document.querySelectorAll('.home__add-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const product = LITUP_PRODUCTS[btn.dataset.id] || findProductByName(btn.dataset.product);

    if (!product) {
      showToast('Product details are unavailable right now.', 'error');
      return;
    }

    void addToCart(
      product.id,
      product.name,
      product.price,
      product.img,
      'One Size',
      1
    );
  });
});

/* ============================================================
   CART PAGE
   ============================================================ */
(function initCartPage() {
  const cartPage = document.querySelector('.cart-page');
  if (!cartPage) return;
  cartPage.setAttribute('aria-live', 'polite');

  function rupeesFromCents(cents) {
    return (cents || 0) / 100;
  }

  async function renderCart() {
    const user = Store.getUser();
    const token = Store.getToken();

    if (!user || !token) {
      cartPage.innerHTML = `
        <div class="cart-empty-state">
          <div class="cart-empty-icon" aria-hidden="true">Cart</div>
          <h2>You're not logged in</h2>
          <p>Log in to view and manage your cart.</p>
          <a href="./account.html" class="btn">Go to Account</a>
        </div>`;
      return;
    }

    let cartData;
    try {
      const json = await apiFetch('/api/cart', { method: 'GET' });
      cartData = json.data;
    } catch (e) {
      cartPage.innerHTML = `
        <div class="cart-empty-state">
          <h2>Could not load cart</h2>
          <p>${e.message || 'Please try again.'}</p>
          <a href="./account.html" class="btn">Account</a>
        </div>`;
      return;
    }

    const items = (cartData && cartData.items) || [];
    if (!items.length) {
      cartPage.innerHTML = `
        <div class="cart-empty-state">
          <div class="cart-empty-icon" aria-hidden="true">Bag</div>
          <h2>Your cart is empty</h2>
          <p>Looks like you haven't added anything yet.</p>
          <a href="./products.html" class="btn">Browse Products</a>
        </div>`;
      return;
    }

    const subtotalCents = cartData.subtotal_cents || 0;
    const subtotalRupees = rupeesFromCents(subtotalCents);
    const shippingRupees = subtotalRupees >= 999 ? 0 : 99;
    const totalRupees = subtotalRupees + shippingRupees;
    const shippingCents = Math.round(shippingRupees * 100);

    cartPage.innerHTML = `
      <h1 class="cart-title">My Cart</h1>
      <div class="cart-layout">
        <div class="cart-items" aria-label="Cart items">
          ${items.map(item => {
            const p = item.product || {};
            const name = p.name || 'Item';
            const img = p.image_url || '';
            const unitRupees = rupeesFromCents(item.unit_price_cents);
            const lineRupees = rupeesFromCents(item.line_total_cents);
            const size = item.size || '—';
            return `
            <article class="cart-item" data-item-id="${item.id}">
              <div class="cart-item-img-wrap">
                ${img ? `<img src="${img}" alt="${name}">` : '<div class="cart-item-no-img" aria-hidden="true">Item</div>'}
              </div>
              <div class="cart-item-info">
                <h2>${name}</h2>
                <p class="cart-item-meta">Size: <span>${size}</span></p>
                <p class="cart-item-price">\u20B9${unitRupees.toLocaleString()}</p>
              </div>
              <div class="cart-item-controls">
                <div class="qty-control" aria-label="Quantity controls">
                  <button type="button" class="qty-btn" data-action="dec" data-item-id="${item.id}" aria-label="Decrease quantity for ${name}">-</button>
                  <span aria-live="polite">${item.quantity}</span>
                  <button type="button" class="qty-btn" data-action="inc" data-item-id="${item.id}" aria-label="Increase quantity for ${name}">+</button>
                </div>
                <button type="button" class="remove-btn" data-item-id="${item.id}" aria-label="Remove ${name} from cart">Remove</button>
              </div>
              <div class="cart-item-total">\u20B9${lineRupees.toLocaleString()}</div>
            </article>`;
          }).join('')}
        </div>
        <aside class="cart-summary" aria-label="Order summary">
          <h2>Order Summary</h2>
          <div class="summary-row"><span>Subtotal</span><span>\u20B9${subtotalRupees.toLocaleString()}</span></div>
          <div class="summary-row"><span>Shipping</span><span>${shippingRupees === 0 ? '<span class="free-tag">FREE</span>' : `\u20B9${shippingRupees}`}</span></div>
          <div class="summary-divider"></div>
          <div class="summary-row summary-total">
            <span>Total</span>
            <span>\u20B9${totalRupees.toLocaleString()}</span>
          </div>
          <button type="button" class="btn checkout-btn" id="checkoutBtn" data-shipping-cents="${shippingCents}">Place Order</button>
          <a href="./products.html" class="continue-link">Continue Shopping</a>
          <p class="free-ship-note">${subtotalRupees < 999 ? `Add \u20B9${Math.max(0, 999 - subtotalRupees).toLocaleString()} more for free shipping.` : 'You unlocked free shipping.'}</p>
        </aside>
      </div>`;

    cartPage.querySelector('.cart-items').addEventListener('click', async event => {
      const t = event.target;
      const itemId = t.dataset.itemId ? parseInt(t.dataset.itemId, 10) : null;
      if (!itemId) return;

      const article = t.closest('.cart-item');
      if (!article) return;
      const qtySpan = article.querySelector('.qty-control span[aria-live="polite"]');
      const currentQty = parseInt(qtySpan ? qtySpan.textContent : '0', 10) || 1;

      try {
        if (t.classList.contains('qty-btn')) {
          let nextQty = currentQty;
          if (t.dataset.action === 'inc') nextQty += 1;
          if (t.dataset.action === 'dec') nextQty -= 1;

          await apiFetch('/api/cart/update', {
            method: 'PUT',
            body: JSON.stringify({ item_id: itemId, quantity: nextQty })
          });
          await updateCartBadge();
          await renderCart();
          return;
        }

        if (t.classList.contains('remove-btn')) {
          await apiFetch('/api/cart/remove', {
            method: 'DELETE',
            body: JSON.stringify({ item_id: itemId })
          });
          await updateCartBadge();
          await renderCart();
          showToast('Item removed from cart.', 'info');
        }
      } catch (e) {
        showToast(e.message || 'Update failed.', 'error');
      }
    });

    document.getElementById('checkoutBtn').addEventListener('click', async () => {
      const btn = document.getElementById('checkoutBtn');
      const sc = parseInt(btn.dataset.shippingCents || '0', 10) || 0;
      try {
        await apiFetch('/api/orders/create', {
          method: 'POST',
          body: JSON.stringify({ shipping_cents: sc })
        });
        await updateCartBadge();
        showToast('Order placed successfully.', 'success');
        await renderCart();
      } catch (e) {
        showToast(e.message || 'Checkout failed.', 'error');
      }
    });
  }

  void renderCart();
})();

/* ============================================================
   ACCOUNT PAGE
   ============================================================ */
(function initAccountPage() {
  const authForms = document.getElementById('authForms');
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const logBtn = document.getElementById('removeLog');
  const regBtn = document.getElementById('removeReg');
  const profileSection = document.getElementById('profileSection');

  if (!loginForm && !profileSection) return;

  const user = Store.getUser();
  const token = Store.getToken();

  if (user && token && profileSection) {
    if (authForms) authForms.hidden = true;
    profileSection.hidden = false;

    const nameEl = document.getElementById('profileName');
    const emailEl = document.getElementById('profileEmail');
    if (nameEl) nameEl.textContent = user.username;
    if (emailEl) emailEl.textContent = user.email || '-';
  } else if (loginForm && registerForm) {
    setActiveAuthView('login');
  }

  if (logBtn) logBtn.addEventListener('click', () => setActiveAuthView('login'));
  if (regBtn) regBtn.addEventListener('click', () => setActiveAuthView('register'));

  if (loginForm) {
    loginForm.addEventListener('submit', async event => {
      event.preventDefault();
      const username = loginForm.querySelector('input[name="username"]').value.trim();
      const password = loginForm.querySelector('input[name="password"]').value;

      try {
        const json = await apiFetch('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ username, password, enable_session: true })
        });
        const data = json.data;
        Store.setToken(data.access_token);
        Store.setUser(data.user);
        showToast(`Welcome back, ${data.user.username}.`, 'success');
        setTimeout(() => window.location.reload(), 600);
      } catch (e) {
        showToast(e.message || 'Login failed.', 'error');
      }
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', async event => {
      event.preventDefault();
      const username = registerForm.querySelector('input[name="username"]').value.trim();
      const email = registerForm.querySelector('input[name="email"]').value.trim();
      const password = registerForm.querySelector('input[name="password"]').value;

      if (!username || !email || !password) {
        showToast('Please fill in every field.', 'error');
        return;
      }

      try {
        const json = await apiFetch('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({ username, email, password })
        });
        const data = json.data;
        Store.setToken(data.access_token);
        Store.setUser(data.user);
        showToast(`Account created for ${data.user.username}.`, 'success');
        setTimeout(() => window.location.reload(), 600);
      } catch (e) {
        showToast(e.message || 'Registration failed.', 'error');
      }
    });
  }

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await apiFetch('/api/auth/logout', { method: 'POST', body: '{}' });
      } catch { /* ignore */ }
      Store.clearSession();
      showToast('Logged out successfully.', 'info');
      setTimeout(() => window.location.reload(), 600);
    });
  }
})();

/* ============================================================
   TOAST NOTIFICATIONS
   ============================================================ */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.setAttribute('role', 'status');
    container.setAttribute('aria-live', 'polite');
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

window.showToast = showToast;

/* ============================================================
   SCROLL REVEAL (if library loaded)
   ============================================================ */
if (typeof ScrollReveal !== 'undefined') {
  ScrollReveal().reveal('.childprods', { delay: 100, distance: '30px', origin: 'bottom', interval: 80 });
  ScrollReveal().reveal('.home__content', { delay: 200, distance: '40px', origin: 'left' });
}
