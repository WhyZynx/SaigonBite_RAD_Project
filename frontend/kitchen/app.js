const HUB_ID = 1;
const STATUS_LABELS = {PENDING:'Incoming Orders',CONFIRMED:'Confirmed Orders',PREPARING:'Preparing Orders',READY:'Ready for Pickup',REJECTED:'Rejected'};
const state = {activeStatus:'PENDING',selectedOrderId:null,selectedOrder:null,orders:[],search:'',newestFirst:true,busy:false,detailRequest:0};
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = value => new Intl.NumberFormat('vi-VN').format(Number(value)||0)+' ₫';
const dateText = value => value ? new Date(value).toLocaleString('en-GB',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}) : 'Time unavailable';
const ago = value => {if(!value)return 'Time unavailable';const m=Math.max(0,Math.floor((Date.now()-new Date(value))/60000));return m<1?'Just now':m<60?`${m} min ago`:`${Math.floor(m/60)} hr ago`;};
function showMessage(message,error=false){const box=$('alert');box.textContent=message;box.className=`alert-message ${error?'alert-error':'alert-success'}`;box.hidden=false;clearTimeout(showMessage.timer);showMessage.timer=setTimeout(()=>box.hidden=true,4500);}
async function api(url,options={}){const response=await fetch(url,{headers:{'Content-Type':'application/json'},...options});let data={};try{data=await response.json()}catch{}if(!response.ok)throw new Error(data.detail||`Request failed (${response.status})`);return data;}
function currentOrders(){return state.orders.filter(order=>order.status===state.activeStatus);}
function setActiveStatus(status){state.activeStatus=status;document.querySelectorAll('.nav-link').forEach(button=>button.classList.toggle('active',button.dataset.view===status));$('header-category').textContent=STATUS_LABELS[status];$('page-title').textContent=STATUS_LABELS[status];}
async function refreshOrders({preserveSelection=true}={}){
  const selectedId=preserveSelection?state.selectedOrderId:null;
  $('order-list').innerHTML='<div class="loading">Loading kitchen orders…</div>';
  try{
    const [active,rejected]=await Promise.all([
      api(`/api/kitchen/orders?hub_id=${HUB_ID}`),
      api(`/api/kitchen/orders?hub_id=${HUB_ID}&status=REJECTED`)
    ]);
    const byId=new Map([...active,...rejected].map(order=>[order.id,order]));
    state.orders=[...byId.values()];updateCounts();renderQueue();
    if(selectedId!==null){
      const summary=state.orders.find(order=>order.id===selectedId);
      if(summary){state.selectedOrderId=selectedId;await loadSelectedOrder();return;}
      state.selectedOrderId=null;state.selectedOrder=null;
    }
    state.selectedOrderId=null;state.selectedOrder=null;renderDetails();
  }catch(error){$('order-list').innerHTML=`<div class="empty-list">Could not load orders.<br><small>${esc(error.message)}</small><br><button class="refresh-button" id="retry-load">Try again</button></div>`;$('retry-load')?.addEventListener('click',()=>refreshOrders());}
}
function updateCounts(){for(const status of Object.keys(STATUS_LABELS))$(`count-${status}`).textContent=state.orders.filter(order=>order.status===status).length;}
function renderQueue(){
  const entries=currentOrders().filter(order=>{const search=state.search.trim().toLowerCase();return !search||String(order.id).includes(search)||String(order.customer_id??'').toLowerCase().includes(search)||String(order.customer_name??'').toLowerCase().includes(search);});
  const ordered=state.newestFirst?entries:[...entries].reverse();
  $('queue-count').textContent=`${entries.length} ${state.activeStatus.toLowerCase()} order${entries.length===1?'':'s'}`;$('visible-count').textContent=entries.length;$('queue-footer-count').textContent=`Showing ${entries.length} order${entries.length===1?'':'s'}`;
  if(!ordered.length){$('order-list').innerHTML=`<div class="empty-list">${state.search?'No orders match your search.':`No ${state.activeStatus.toLowerCase()} orders right now.`}</div>`;return;}
  $('order-list').innerHTML=ordered.map(order=>{
    const chosen=state.selectedOrder?.id===order.id?state.selectedOrder:null;
    const customer=order.customer_name||chosen?.customer_name||`Customer #${order.customer_id}`;
    const itemCount=chosen?.items?.reduce((sum,item)=>sum+Number(item.quantity||0),0);
    const itemText=itemCount?`${itemCount} item${itemCount===1?'':'s'}`:'Order details';
    return `<article class="order-card ${order.id===state.selectedOrderId?'selected':''}" data-id="${order.id}" tabindex="0" role="button" aria-label="Open order ${order.id}"><div class="order-top"><span class="order-id">#SB-${order.id}</span><span class="badge-status status-${order.status}">${order.status==='READY'?'READY FOR PICKUP':order.status}</span></div><div class="order-customer"><span>${esc(customer)}</span><span class="order-age">${esc(ago(order.created_at))}</span></div><div class="order-bottom"><span class="item-preview">${itemText}</span><span class="order-total">${money(order.total)}</span></div></article>`;
  }).join('');
  $('order-list').querySelectorAll('.order-card').forEach(card=>{const open=()=>selectOrder(Number(card.dataset.id));card.addEventListener('click',open);card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open();}});});
}
async function selectOrder(id){state.selectedOrderId=id;state.selectedOrder=null;renderQueue();document.body.classList.add('detail-open');await loadSelectedOrder();}
async function loadSelectedOrder(){
  const id=state.selectedOrderId;if(id===null){renderDetails();return;}
  const requestId=++state.detailRequest;$('detail-panel').innerHTML='<div class="loading detail-empty">Loading order details…</div>';
  try{const order=await api(`/api/orders/${id}`);if(requestId!==state.detailRequest||state.selectedOrderId!==id)return;state.selectedOrder=order;renderQueue();renderDetails();}
  catch(error){if(requestId!==state.detailRequest)return;state.selectedOrder=null;$('detail-panel').innerHTML=`<div class="detail-empty"><h2>Order unavailable</h2><p>${esc(error.message)}</p><button class="refresh-button" id="retry-detail">Retry</button></div>`;$('retry-detail')?.addEventListener('click',loadSelectedOrder);}
}
function renderDetails(){
  const order=state.selectedOrder;
  if(!order){$('detail-panel').innerHTML='<div class="detail-empty"><div class="empty-illustration">▤</div><h2>Select an order</h2><p>Choose an order from the queue to review its details.</p></div>';return;}
  const status=order.status;
  const customerName=order.customer_name||order.customer?.name;
  const customerPhone=order.customer_phone||order.phone||order.customer?.phone;
  const note=order.customer_note||order.special_note||order.note;
  const itemRows=(order.items||[]).map(item=>`<div class="dish-row"><div><div class="dish-name"><span class="quantity-badge">${Number(item.quantity)||0}</span>${esc(item.name)}</div>${item.options?.length?`<span class="dish-options">${esc(item.options.join(', '))}</span>`:''}<div class="dish-sub">${money(item.unit_price)} each</div></div><div class="dish-price">${money(item.line_total)}</div></div>`).join('');
  const customerInfo=`${customerName?`<div class="customer-field"><small>NAME</small><strong>${esc(customerName)}</strong></div>`:''}${customerPhone?`<div class="customer-field"><small>PHONE</small><strong>${esc(customerPhone)}</strong></div>`:''}<div class="customer-field customer-address"><small>DELIVERY ADDRESS</small><strong>${esc(order.delivery_address||'Address unavailable')}</strong></div>`;
  const actions=status==='PENDING'?'<button class="action-btn reject-btn" data-action="reject">Reject Order</button><button class="action-btn accept-btn" data-action="confirm">Accept Order　→</button>':status==='CONFIRMED'?'<button class="action-btn prepare-btn" data-action="prepare">Start Preparing　→</button>':status==='PREPARING'?'<button class="action-btn ready-btn" data-action="ready">Mark Ready　✓</button>':'';
  const readOnly=status==='READY'?'<div class="read-only">✓　Order is ready for pickup.</div>':status==='REJECTED'?`<div class="read-only">Order rejected${order.rejection_reason?`<div class="rejection-box"><strong>Reason</strong><br>${esc(order.rejection_reason)}</div>`:''}</div>`:'';
  $('detail-panel').innerHTML=`<div class="detail-scroll"><button class="back-orders" id="back-orders">← Back to Orders</button><div class="detail-head"><div><h2>Order #SB-${order.id}</h2><p>Placed ${esc(dateText(order.created_at))}</p>${order.delivery_distance_km!=null?`<div class="delivery-line">⌖　Delivery · ${esc(order.delivery_distance_km)} km</div>`:''}</div><span class="badge-status status-${status}">${status==='READY'?'READY FOR PICKUP':status}</span></div><section class="detail-section dishes-section"><h3 class="section-title">Ordered Dishes <span>${(order.items||[]).reduce((total,item)=>total+(Number(item.quantity)||0),0)} items</span></h3>${itemRows||'<div class="special-note">Order items unavailable.</div>'}</section><section class="detail-section note-section"><h3 class="section-title">Special Note From Customer</h3><div class="special-note">${note?esc(note):'No special instructions'}</div></section><section class="detail-section customer-section"><h3 class="section-title">Customer Information</h3><div class="customer-grid">${customerInfo}</div></section><section class="detail-section summary-section"><h3 class="section-title">Order Summary</h3><div class="summary-row"><span>Subtotal</span><span>${money(order.subtotal)}</span></div>${Number(order.delivery_fee)?`<div class="summary-row"><span>Delivery fee</span><span>${money(order.delivery_fee)}</span></div>`:''}${Number(order.surcharge)?`<div class="summary-row"><span>Other charges</span><span>${money(order.surcharge)}</span></div>`:''}${Number(order.discount)?`<div class="summary-row"><span>Discount</span><span>− ${money(order.discount)}</span></div>`:''}<div class="summary-row total"><span>Total</span><span>${money(order.total)}</span></div><div class="payment-grid"><div><small>PAYMENT METHOD</small><strong>${esc(order.payment_method||'Unavailable')}</strong></div><div><small>PAYMENT STATUS</small><strong>${esc(order.payment_status||'Unavailable')}</strong></div></div></section><section class="detail-section history-section"><h3 class="section-title">Order History</h3><div class="history-list">${(order.status_history||[]).map(entry=>`<div class="history-row"><span class="history-dot"></span><span>${esc(entry.status==='READY'?'Ready for Pickup':entry.status)}${entry.note?` <span class="history-note">· ${esc(entry.note)}</span>`:''}</span><time class="history-time">${esc(dateText(entry.changed_at))}</time></div>`).join('')}</div></section>${status==='REJECTED'&&!order.rejection_reason?'<div class="rejection-box">Rejection reason is unavailable.</div>':''}</div>${actions?`<footer class="detail-actions">${actions}</footer>`:readOnly}`;
  $('back-orders')?.addEventListener('click',()=>{document.body.classList.remove('detail-open');});
  $('detail-panel').querySelector('[data-action="reject"]')?.addEventListener('click',openRejectDialog);
  $('detail-panel').querySelector('[data-action="confirm"]')?.addEventListener('click',()=>changeStatus(`/api/kitchen/orders/${order.id}/decision`,{decision:'CONFIRM'},'CONFIRMED','Order accepted.'));
  $('detail-panel').querySelector('[data-action="prepare"]')?.addEventListener('click',()=>changeStatus(`/api/kitchen/orders/${order.id}/status`,{status:'PREPARING'},'PREPARING','Preparation started.'));
  $('detail-panel').querySelector('[data-action="ready"]')?.addEventListener('click',()=>changeStatus(`/api/kitchen/orders/${order.id}/status`,{status:'READY'},'READY','Order marked ready for pickup.'));
}
function setBusy(busy){state.busy=busy;$('detail-panel').querySelectorAll('.action-btn').forEach(button=>{if(busy){button.dataset.originalText=button.textContent;button.disabled=true;button.textContent='Updating…';}else{button.disabled=false;if(button.dataset.originalText)button.textContent=button.dataset.originalText;}});}
async function changeStatus(url,payload,nextStatus,message){if(state.busy)return;const orderId=state.selectedOrderId;setBusy(true);try{await api(url,{method:'PATCH',body:JSON.stringify(payload)});state.busy=false;state.selectedOrderId=orderId;state.activeStatus=nextStatus;setActiveStatus(nextStatus);await refreshOrders({preserveSelection:true});showMessage(message);}
  catch(error){setBusy(false);showMessage(error.message,true);}}
function openRejectDialog(){const order=state.selectedOrder;$('reject-order-id').textContent=`Order #SB-${order.id}`;$('reject-reason').value='';$('reason-error').hidden=true;$('rejectModal').classList.add('show');$('rejectModal').setAttribute('aria-hidden','false');$('reject-reason').focus();}
function closeRejectDialog(){$('rejectModal').classList.remove('show');$('rejectModal').setAttribute('aria-hidden','true');}
$('rejectModal').querySelectorAll('[data-bs-dismiss="modal"]').forEach(button=>button.addEventListener('click',closeRejectDialog));$('rejectModal').addEventListener('click',event=>{if(event.target===$('rejectModal'))closeRejectDialog();});
$('submit-reject').addEventListener('click',async()=>{if(state.busy)return;const reason=$('reject-reason').value.trim();if(!reason){$('reason-error').hidden=false;$('reject-reason').focus();return;}const orderId=state.selectedOrderId;const button=$('submit-reject');button.disabled=true;button.textContent='Rejecting…';try{await api(`/api/kitchen/orders/${orderId}/decision`,{method:'PATCH',body:JSON.stringify({decision:'REJECT',reason})});state.selectedOrderId=orderId;state.activeStatus='REJECTED';setActiveStatus('REJECTED');closeRejectDialog();await refreshOrders({preserveSelection:true});showMessage('Order rejected. Reason recorded.');}catch(error){$('reason-error').textContent=error.message;$('reason-error').hidden=false;}finally{button.disabled=false;button.innerHTML='Reject order <span>→</span>';}});
document.querySelectorAll('.nav-link').forEach(button=>button.addEventListener('click',()=>{state.selectedOrderId=null;state.selectedOrder=null;state.detailRequest++;state.activeStatus=button.dataset.view;setActiveStatus(state.activeStatus);renderQueue();renderDetails();document.body.classList.remove('detail-open');$('sidebar').classList.remove('drawer-open');$('drawer-scrim').classList.remove('visible');}));
$('search').addEventListener('input',event=>{state.search=event.target.value;renderQueue();});$('refresh').addEventListener('click',()=>refreshOrders());$('sort-btn').addEventListener('click',()=>{state.newestFirst=!state.newestFirst;$('sort-btn').textContent=state.newestFirst?'Newest first⌄':'Oldest first⌄';renderQueue();});
$('mobile-menu').addEventListener('click',()=>{$('sidebar').classList.add('drawer-open');$('drawer-scrim').classList.add('visible');});$('drawer-scrim').addEventListener('click',()=>{$('sidebar').classList.remove('drawer-open');$('drawer-scrim').classList.remove('visible');});$('logout').addEventListener('click',()=>showMessage('Logout will be available when kitchen authentication is integrated.',true));
document.addEventListener('keydown',event=>{if(event.key==='/'&&!['INPUT','TEXTAREA'].includes(document.activeElement.tagName)){event.preventDefault();$('search').focus();}if(event.key==='Escape'){$('sidebar').classList.remove('drawer-open');$('drawer-scrim').classList.remove('visible');closeRejectDialog();}});
setActiveStatus(state.activeStatus);refreshOrders({preserveSelection:false});
