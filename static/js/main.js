document.addEventListener('DOMContentLoaded', function() {
    // 用戶下拉選單
    const userDropdown = document.querySelector('.user-dropdown');
    if (userDropdown) {
        userDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('active');
        });
        
        document.addEventListener('click', function() {
            userDropdown.classList.remove('active');
        });
    }
    
    // 表單驗證
    const authForms = document.querySelectorAll('.auth-form');
    authForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const password1 = form.querySelector('input[name="password1"]');
            const password2 = form.querySelector('input[name="password2"]');
            
            if (password1 && password2) {
                if (password1.value !== password2.value) {
                    e.preventDefault();
                    alert('密碼不匹配，請重新輸入');
                    return false;
                }
                
                if (password1.value.length < 8) {
                    e.preventDefault();
                    alert('密碼長度至少需要8個字符');
                    return false;
                }
            }
        });
    });
    
    // 頭像上傳預覽
    const avatarUpload = document.getElementById('avatar-upload');
    if (avatarUpload) {
        avatarUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const avatarCircle = document.querySelector('.avatar-circle');
                    avatarCircle.innerHTML = `<img src="${e.target.result}" alt="頭像預覽" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // 訊息自動消失
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // 搜索按鈕事件綁定
    const searchBtn = document.querySelector('.search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', searchAttractions);
    }
    
    // 搜索輸入框回車事件
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchAttractions();
            }
        });
    }
    
    // 篩選器變更事件
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', searchAttractions);
    });
    
    // 初始化加入行程按鈕事件
    bindAddToPlanEvents();
});

// 標籤頁切換功能
function switchTab(tabName) {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// 行程管理功能
function editTrip(tripId) {
    // 這裡可以開啟編輯行程的模態框或跳轉到編輯頁面
    window.location.href = `/trip/edit/${tripId}/`;
}

function deleteTrip(tripId) {
    if (confirm('確定要刪除這個行程嗎？')) {
        fetch(`/trip/delete/${tripId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('刪除失敗，請稍後再試');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('發生錯誤，請稍後再試');
        });
    }
}

// 搜索功能
function searchAttractions() {
    const searchInput = document.querySelector('.search-input');
    const regionSelect = document.querySelector('.filter-select:nth-child(2)');
    const typeSelect = document.querySelector('.filter-select:nth-child(3)');
    const ratingSelect = document.querySelector('.filter-select:nth-child(4)');
    
    // 檢查元素是否存在，避免錯誤
    const searchValue = searchInput ? searchInput.value : '';
    const regionValue = regionSelect ? regionSelect.value : '';
    const typeValue = typeSelect ? typeSelect.value : '';
    const ratingValue = ratingSelect ? ratingSelect.value : '';
    
    const params = new URLSearchParams({
        search: searchValue,
        region: regionValue,
        type: typeValue,
        rating: ratingValue
    });
    
    // 顯示載入狀態
    showLoading();
    
    fetch(`/search-attractions/?${params}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            if (data.success) {
                updateAttractionsGrid(data.attractions);
            } else {
                alert(data.message || '搜索失敗，請稍後再試');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('搜索錯誤:', error);
            alert('搜索時發生錯誤，請檢查網路連接');
        });
}

// 更新景點網格
function updateAttractionsGrid(attractions) {
    const grid = document.querySelector('.attractions-grid');
    if (!grid) return;
    
    // 清空現有內容
    grid.innerHTML = '';
    
    if (attractions.length === 0) {
        grid.innerHTML = '<div class="no-results">未找到符合條件的景點</div>';
        return;
    }
    
    attractions.forEach(attraction => {
        const card = document.createElement('div');
        card.className = 'attraction-card';
        card.innerHTML = `
            <img src="${attraction.image || '/static/images/default-attraction.jpg'}" 
                 alt="${attraction.name}" 
                 class="attraction-image"
                 onerror="this.src='/static/images/default-attraction.jpg'">
            <div class="attraction-info">
                <div class="attraction-name">${attraction.name}</div>
                <div class="attraction-location">${attraction.location}</div>
                <div class="attraction-rating">${attraction.rating_stars} ${attraction.rating}</div>
                <button class="add-to-plan-btn" data-attraction-id="${attraction.id}">加入行程</button>
            </div>
        `;
        grid.appendChild(card);
    });
    
    // 重新綁定事件
    bindAddToPlanEvents();
}

// 綁定加入行程按鈕事件
function bindAddToPlanEvents() {
    document.querySelectorAll('.add-to-plan-btn').forEach(btn => {
        // 移除舊的事件監聽器（如果存在）
        btn.removeEventListener('click', handleAddToPlan);
        // 添加新的事件監聽器
        btn.addEventListener('click', handleAddToPlan);
    });
}

// 處理加入行程按鈕點擊
function handleAddToPlan(event) {
    const button = event.target;
    const attractionId = button.getAttribute('data-attraction-id');
    
    if (!attractionId) {
        alert('景點ID錯誤');
        return;
    }
    
    addToTrip(attractionId, button);
}

// 加入行程功能
function addToTrip(attractionId, button) {
    // 禁用按鈕防止重複點擊
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = '加入中...';
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        alert('CSRF token 未找到，請重新載入頁面');
        button.disabled = false;
        button.textContent = originalText;
        return;
    }
    
    fetch(`/add-to-plan/${attractionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken.value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            attraction_id: attractionId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // 成功動畫
            button.style.background = '#28a745';
            button.textContent = '已加入';
            
            // 2秒後恢復原狀
            setTimeout(() => {
                button.style.background = '#ff69b4';
                button.textContent = originalText;
                button.disabled = false;
            }, 2000);
            
            // 更新行程列表
            updateTripList();
            
            // 顯示成功訊息
            showMessage('景點已成功加入行程！', 'success');
        } else {
            throw new Error(data.message || '加入失敗');
        }
    })
    .catch(error => {
        console.error('加入行程錯誤:', error);
        alert(error.message || '加入行程時發生錯誤，請稍後再試');
        button.disabled = false;
        button.textContent = originalText;
    });
}

// 更新行程列表
function updateTripList() {
    fetch('/get-user-trips/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tripContainer = document.querySelector('.my-itinerary');
                if (tripContainer && data.trips) {
                    // 更新行程列表的邏輯
                    updateTripContainer(data.trips);
                }
            }
        })
        .catch(error => {
            console.error('更新行程列表錯誤:', error);
        });
}

// 更新行程容器
function updateTripContainer(trips) {
    const container = document.querySelector('.my-itinerary');
    if (!container) return;
    
    // 保留標題
    const title = container.querySelector('.itinerary-title');
    container.innerHTML = '';
    if (title) {
        container.appendChild(title);
    }
    
    trips.forEach(trip => {
        const tripElement = document.createElement('div');
        tripElement.className = 'itinerary-item';
        tripElement.innerHTML = `
            <div class="itinerary-date">${trip.title}</div>
            <div class="itinerary-details">
                <div>
                    <div class="trip-dates">${trip.start_date} - ${trip.end_date}</div>
                    <div class="trip-attractions">已規劃景點: ${trip.attraction_count}</div>
                </div>
                <div class="itinerary-actions">
                    <button class="btn-small btn-edit" onclick="editTrip(${trip.id})">編輯</button>
                    <button class="btn-small btn-delete" onclick="deleteTrip(${trip.id})">刪除</button>
                </div>
            </div>
        `;
        container.appendChild(tripElement);
    });
}

// 顯示載入狀態
function showLoading() {
    const grid = document.querySelector('.attractions-grid');
    if (grid) {
        grid.innerHTML = '<div class="loading">搜索中...</div>';
    }
}

// 隱藏載入狀態
function hideLoading() {
    const loading = document.querySelector('.loading');
    if (loading) {
        loading.remove();
    }
}

// 顯示訊息
function showMessage(message, type = 'info') {
    const messageContainer = document.querySelector('.messages') || createMessageContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        ${message}
        <button class="close-btn" onclick="this.parentElement.remove()">×</button>
    `;
    
    messageContainer.appendChild(alertDiv);
    
    // 5秒後自動移除
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

// 創建訊息容器
function createMessageContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(container, mainContent.firstChild);
    } else {
        document.body.insertBefore(container, document.body.firstChild);
    }
    
    return container;
}

// 表單提交增強
function enhanceFormSubmission() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '提交中...';
                
                // 如果提交失敗，恢復按鈕狀態
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.getAttribute('data-original-text') || '提交';
                }, 5000);
            }
        });
    });
}

// 初始化時保存按鈕原始文字
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        btn.setAttribute('data-original-text', btn.textContent);
    });
    
    enhanceFormSubmission();
});

// 錯誤處理
window.addEventListener('error', function(e) {
    console.error('JavaScript 錯誤:', e.error);
});

// 未處理的 Promise 拒絕
window.addEventListener('unhandledrejection', function(e) {
    console.error('未處理的 Promise 拒絕:', e.reason);
});