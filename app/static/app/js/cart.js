var updateBtns = document.getElementsByClassName('update-cart')

for(i = 0;i < updateBtns.length;i++){
  updateBtns[i].addEventListener('click',function() {
    var productId = this.dataset.product
    var action = this.dataset.action
    console.log('productId', productId,'action',action)
    console.log('user:',user)
    if  (user === "AnonymousUser"){
      console.log('user not logged in')
    } else {
      updateUserOrder(productId,action)
    }
  })
}

function updateUserOrder(productId,action){
  console.log('user logged in, success add')
  var url ='/update_item/'
  fetch(url ,{
    method: 'POST',
    headers:{
      'Content-Type':'application/json',
      'X-CSRFToken':csrftoken,
    },
    body: JSON.stringify({'productId':productId,'action':action})
  })
  .then((response) => {
    // Kiểm tra trạng thái HTTP
    if (!response.ok) {
      return response.json().then((data) => {
        // Xử lý lỗi cụ thể từ server
        if (data.error) {
          alert(data.error); // Hiển thị thông báo lỗi cụ thể
        }
        throw new Error(data.error || `HTTP Error: ${response.status}`);
      });
    }
    return response.json();
  })

  .then((data) =>{
    console.log('data',data)
    if(action!='watch'){
      location.reload()
    }
  })
}