const cart = [];
const dialog = document.querySelector('#cart-dialog');
const yen = value => `¥${value.toLocaleString('ja-JP')}`;

function renderCart() {
  const list = document.querySelector('#cart-items');
  list.innerHTML = cart.map((item, index) => `<div class="cart-item"><div><strong>${item.name}</strong><p>SIZE ${item.size}</p><p>${yen(item.price)}</p></div><button data-remove="${index}">削除</button></div>`).join('');
  document.querySelectorAll('[data-remove]').forEach(button => button.onclick = () => { cart.splice(Number(button.dataset.remove), 1); renderCart(); });
  const count = cart.length;
  document.querySelector('#cart-count').textContent = count;
  document.querySelector('#cart-total-items').textContent = count;
  document.querySelector('#cart-total').textContent = yen(cart.reduce((sum, item) => sum + item.price, 0));
  document.querySelector('#cart-empty').hidden = count > 0;
  document.querySelector('#cart-summary').hidden = count === 0;
}

document.querySelectorAll('.add-cart').forEach(button => button.addEventListener('click', () => {
  const card = button.closest('.product-card');
  cart.push({ name: card.dataset.name, price: Number(card.dataset.price), size: card.querySelector('select').value });
  renderCart();
  const toast = document.querySelector('#toast');
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 1600);
}));

document.querySelector('#open-cart').onclick = () => dialog.showModal();
document.querySelector('#close-cart').onclick = () => dialog.close();
document.querySelector('#newsletter-form').addEventListener('submit', event => {
  event.preventDefault();
  document.querySelector('#newsletter-message').textContent = '登録ありがとうございます。次のニュースをお楽しみに。';
  event.currentTarget.reset();
});
renderCart();
