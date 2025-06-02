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

// 更新搜索結果的景點卡片生成函數
function updateAttractionsGrid(attractions) {
    const grid = document.querySelector('.attractions-grid');
    if (!grid) return;
    
    // 清空現有內容
    grid.innerHTML = '';
    
    if (attractions.length === 0) {
        grid.innerHTML = '<div class="no-results">未找到符合條件的景點</div>';
        return;
    }
    
    // 查看景點詳情函數
    function viewAttractionDetail(attractionId) {
        window.location.href = `/card/${attractionId}/`;
    }


    // 預設圖片映射
    const defaultImages = {
        '寺廟神社': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=300&h=180&fit=crop',
        '現代景點': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=300&h=180&fit=crop',
        '自然風光': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=300&h=180&fit=crop',
        '美食': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=300&h=180&fit=crop',
        '購物娛樂': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=180&fit=crop',
        'default': 'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=300&h=180&fit=crop'
    };
    
    attractions.forEach(attraction => {
        const card = document.createElement('div');
        card.className = 'attraction-card';
        card.onclick = () => viewAttractionDetail(attraction.id);
        
        // 選擇預設圖片
        let defaultImg = defaultImages['default'];
        if (attraction.type && defaultImages[attraction.type]) {
            defaultImg = defaultImages[attraction.type];
        }
        
        card.innerHTML = `
            <img src="${attraction.image || defaultImg}" 
                 alt="${attraction.name}" 
                 class="attraction-image"
                 onerror="this.src='${defaultImg}'">
            <div class="attraction-info">
                <div class="attraction-name">${attraction.name}</div>
                <div class="attraction-location">${attraction.location}</div>
                <div class="attraction-rating">${attraction.rating_stars} ${attraction.rating}</div>
                <button class="view-detail-btn" onclick="event.stopPropagation(); viewAttractionDetail(${attraction.id})">查看詳情</button>
            </div>
        `;
        grid.appendChild(card);
    });
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

    addToTrip(button);
}

// 加入行程功能
function addToTrip(button) {
    console.log('=== addToTrip 開始 ===');
    
    // 獲取必要的數值
    const tripId = document.getElementById('trip-select').value;
    const selectedDate = document.getElementById('date-select').value;
    const rememberChoice = document.getElementById('remember-trip').checked;
    
    console.log('tripId:', tripId);
    console.log('selectedDate:', selectedDate);
    console.log('rememberChoice:', rememberChoice);
    
    if (!tripId || !selectedDate) {
        alert('請選擇行程和日期');
        return;
    }
    
    // 從按鈕獲取景點 ID
    const attractionId = button.getAttribute('data-attraction-id');
    if (!attractionId) {
        alert('景點 ID 未找到，請重新載入頁面');
        return;
    }
    
    console.log('attractionId:', attractionId);
    
    // 禁用按鈕防止重複點擊
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = '加入中...';
    
    // 獲取 CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        alert('CSRF token 未找到，請重新載入頁面');
        button.disabled = false;
        button.textContent = originalText;
        return;
    }
    
    // 發送請求
    fetch('/add-attraction-to-trip/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken.value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            attraction_id: attractionId,
            trip_id: tripId,
            selected_date: selectedDate,
            remember_choice: rememberChoice
        })
    })
    .then(response => {
        console.log('響應狀態:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('伺服器響應:', data);
        
        if (data.success) {
            // 保存用戶偏好
            if (rememberChoice) {
                localStorage.setItem('preferred_trip_id', tripId);
            }
            
            // 顯示成功訊息
            if (typeof showMessage === 'function') {
                showMessage(data.message, 'success');
            }
            
            // 更新按鈕狀態
            button.style.background = '#28a745';
            button.textContent = '已加入';
            
            // 1秒後自動跳轉到行程編輯頁面
            setTimeout(() => {
                console.log('準備跳轉到:', `/trip/edit/${tripId}/`);
                window.location.href = `/trip/edit/${tripId}/`;
            }, 1000);
            
        } else {
            alert(data.message || '加入行程失敗');
            button.disabled = false;
            button.textContent = originalText;
        }
    })
    .catch(error => {
        console.error('加入行程請求失敗:', error);
        alert('加入行程失敗，請稍後再試');
        button.disabled = false;
        button.textContent = originalText;
    });
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
            if (typeof updateTripList === 'function') {
                updateTripList();
            }
            
            // 顯示成功訊息
            if (typeof showMessage === 'function') {
                showMessage('景點已成功加入行程！', 'success');
            }
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


function editTrip(tripId) {
    window.location.href = `/trip/edit/${tripId}/`;
}

function deleteTrip(tripId) {
    if (confirm('確定要刪除這個行程嗎？此操作無法復原。')) {
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
                alert(data.message);
                location.reload();
            } else {
                alert(data.message || '刪除失敗，請稍後再試');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('發生錯誤，請稍後再試');
        });
    }
}

function editTrip(tripId) {
    window.location.href = `/trip/edit/${tripId}/`;
}

function deleteTrip(tripId) {
    if (confirm('確定要刪除這個行程嗎？此操作無法復原。')) {
        // 獲取 CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') || 
                         document.querySelector('meta[name=csrf-token]');
        
        if (!csrfToken) {
            alert('安全驗證失敗，請刷新頁面後重試');
            return;
        }
        
        fetch(`/trip/delete/${tripId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken.value || csrfToken.getAttribute('content'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 顯示成功訊息
                showMessage(data.message, 'success');
                // 移除該行程卡片（動態更新）
                const tripCard = document.querySelector(`[onclick="deleteTrip(${tripId})"]`).closest('.trip-card');
                if (tripCard) {
                    tripCard.style.transition = 'all 0.3s ease';
                    tripCard.style.opacity = '0';
                    tripCard.style.transform = 'translateX(-100%)';
                    setTimeout(() => {
                        tripCard.remove();
                        // 檢查是否沒有行程了
                        if (document.querySelectorAll('.trip-card').length === 0) {
                            location.reload();
                        }
                    }, 300);
                }
            } else {
                alert(data.message || '刪除失敗，請稍後再試');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('發生錯誤，請稍後再試');
        });
    }
}

// 顯示訊息的輔助函數
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.innerHTML = `
        ${message}
        <button class="close-btn" onclick="this.parentElement.remove()">×</button>
    `;
    
    const container = document.querySelector('.messages') || createMessageContainer();
    container.appendChild(messageDiv);
    
    // 3秒後自動移除
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, 3000);
}

// 更新景點時間（修改版 - 支援即時排序）
function updateAttractionTime(itineraryAttractionId, newTime) {
    fetch('/update-attraction-time/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            itinerary_attraction_id: itineraryAttractionId,
            new_time: newTime
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('時間已更新', 'success');
            
            // 如果返回了排序資料，立即重新排序
            if (data.sorted_attractions) {
                reorderAttractions(data.sorted_attractions, data.itinerary_date);
            }
        } else {
            alert(data.message || '時間更新失敗');
        }
    })
    .catch(error => {
        console.error('更新時間失敗:', error);
        alert('時間更新失敗，請稍後再試');
    });
}

// 重新排序景點函數
function reorderAttractions(sortedAttractions, itineraryDate) {
    // 根據日期找到對應的天數
    const tripStartDate = new Date('{{ trip.start_time|date:"Y-m-d" }}');
    const currentDate = new Date(itineraryDate);
    const dayDiff = Math.floor((currentDate - tripStartDate) / (1000 * 60 * 60 * 24)) + 1;
    
    const dayContainer = document.getElementById(`day-${dayDiff}-attractions`);
    if (!dayContainer) return;
    
    // 保存空狀態元素
    const emptyDay = dayContainer.querySelector('.empty-day');
    
    // 清空容器
    dayContainer.innerHTML = '';
    
    if (sortedAttractions.length === 0) {
        // 如果沒有景點，顯示空狀態
        if (emptyDay) {
            dayContainer.appendChild(emptyDay);
        } else {
            dayContainer.innerHTML = `
                <div class="empty-day">
                    <p>這天還沒有安排景點</p>
                    <p class="empty-hint">從左側選擇景點並設定為第${dayDiff}天</p>
                </div>
            `;
        }
        return;
    }
    
    // 重新生成排序後的景點列表
    sortedAttractions.forEach(attraction => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'itinerary-item';
        itemDiv.setAttribute('data-attraction-id', attraction.id);
        
        // 選擇合適的預設圖片
        let imageUrl = attraction.image_url;
        if (!imageUrl) {
            const defaultImages = {
                '寺廟神社': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=60&h=60&fit=crop',
                '現代景點': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=60&h=60&fit=crop',
                '自然風光': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=60&h=60&fit=crop',
                '美食': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=60&h=60&fit=crop',
                '購物娛樂': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=60&h=60&fit=crop'
            };
            imageUrl = defaultImages[attraction.attraction_type] || 'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=60&h=60&fit=crop';
        }
        
        itemDiv.innerHTML = `
            <div class="item-image">
                <img src="${imageUrl}" alt="${attraction.name}">
            </div>
            <div class="item-info">
                <div class="item-name">${attraction.name}</div>
                <div class="item-location">${attraction.address}</div>
                <div class="item-controls">
                    <span>天數：</span>
                    <select class="day-change-select" onchange="changeDayForAttraction(${attraction.id}, this.value)">
                        {% for d in trip_days %}
                            <option value="{{ d }}" ${d == dayDiff ? 'selected' : ''}>第{{ d }}天</option>
                        {% endfor %}
                    </select>
                    <span>⏰</span>
                    <input type="time" 
                           class="time-input" 
                           value="${attraction.visit_time}" 
                           onchange="updateAttractionTime(${attraction.id}, this.value)">
                </div>
            </div>
            <div class="item-actions">
                <button class="remove-btn" onclick="removeFromItinerary(${attraction.id})">🗑️</button>
            </div>
        `;
        
        dayContainer.appendChild(itemDiv);
    });
    
    // 添加淡入動畫效果
    dayContainer.style.opacity = '0';
    setTimeout(() => {
        dayContainer.style.transition = 'opacity 0.3s ease';
        dayContainer.style.opacity = '1';
    }, 50);
}

// 修改 addToItinerary 函數，加入後也要重新排序
function addToItinerary(attractionId) {
    const daySelect = document.querySelector(`[data-attraction-id="${attractionId}"]`);
    const selectedDay = daySelect.value;
    
    // 禁用按鈕防止重複點擊
    const addBtn = daySelect.parentElement.querySelector('.add-btn');
    addBtn.disabled = true;
    addBtn.textContent = '加入中...';
    
    fetch('/add-to-itinerary/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            trip_id: {{ trip.id }},
            attraction_id: attractionId,
            day: selectedDay
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // 重新載入頁面以顯示更新和正確排序
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert(data.message || '加入行程失敗');
            addBtn.disabled = false;
            addBtn.textContent = '+ 加入行程';
        }
    })
    .catch(error => {
        console.error('加入行程請求失敗:', error);
        alert('加入行程失敗，請稍後再試');
        addBtn.disabled = false;
        addBtn.textContent = '+ 加入行程';
    });
}

// ========== 收藏功能相關函數 ==========

// 切換收藏狀態
function toggleFavorite(attractionId, button) {
    const heartIcon = button.querySelector('.heart-icon');
    const isFavorited = button.classList.contains('favorited');
    
    // 獲取 CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        alert('安全驗證失敗，請刷新頁面後重試');
        return;
    }
    
    // 禁用按鈕防止重複點擊
    element.style.pointerEvents = 'none';
    
    fetch('/toggle-favorite/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken.value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            attraction_id: attractionId
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('收藏響應:', data);
        
        if (data.success) {
            // 更新愛心圖示狀態
            updateFavoriteButton(element, data.is_favorited);
            
            // 顯示提示訊息
            const message = data.is_favorited ? '已加入收藏' : '已取消收藏';
            showMessage(message, 'success');
            
        } else {
            alert(data.message || '收藏操作失敗');
        }
    })
    .catch(error => {
        console.error('收藏操作失敗:', error);
        alert('收藏操作失敗，請稍後再試');
    })
    .finally(() => {
        // 重新啟用按鈕
        element.style.pointerEvents = 'auto';
    });
}

// 更新收藏按鈕狀態
function updateFavoriteButton(element, isFavorited) {
    if (isFavorited) {
        element.innerHTML = '❤️'; // 實心紅色愛心
        element.classList.add('favorited');
        element.style.color = '#ff1744';
    } else {
        element.innerHTML = '🤍'; // 空心白色愛心
        element.classList.remove('favorited');
        element.style.color = '#999';
    }
}

// 查看收藏列表
function viewFavorites() {
    window.location.href = '/favorites/';
}

// 導航到景點詳情（從收藏頁面）
function navigateToAttractionFromFavorites(attractionId) {
    console.log('導航到景點:', attractionId);
    window.location.href = `/attraction/${attractionId}/`;
}

// 從收藏列表移除景點
function removeFromFavorites(attractionId, element) {
    event.stopPropagation();
    
    if (!confirm('確定要從收藏中移除這個景點嗎？')) {
        return;
    }
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        alert('安全驗證失敗，請刷新頁面後重試');
        return;
    }
    
    fetch('/remove-from-favorites/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken.value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            attraction_id: attractionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 找到景點卡片並移除
            const card = element.closest('.favorite-card, .attraction-card');
            if (card) {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '0';
                card.style.transform = 'translateY(-20px)';
                
                setTimeout(() => {
                    card.remove();
                    
                    // 檢查是否還有收藏的景點
                    const remainingCards = document.querySelectorAll('.favorite-card, .attraction-card');
                    if (remainingCards.length === 0) {
                        showEmptyFavoritesMessage();
                    }
                }, 300);
            }
            
            showMessage('已從收藏中移除', 'success');
        } else {
            alert(data.message || '移除失敗');
        }
    })
    .catch(error => {
        console.error('移除收藏失敗:', error);
        alert('移除失敗，請稍後再試');
    });
}

// 顯示空收藏訊息
function showEmptyFavoritesMessage() {
    const container = document.querySelector('.favorites-grid, .attractions-grid');
    if (container) {
        container.innerHTML = `
            <div class="empty-favorites">
                <div class="empty-icon">💔</div>
                <h3>還沒有收藏的景點</h3>
                <p>快去發現一些美麗的景點並加入收藏吧！</p>
                <button onclick="window.location.href='/'" class="btn-primary">
                    探索景點
                </button>
            </div>
        `;
    }
}

// ========== 更新現有函數以支援收藏功能 ==========

// 修改 updateAttractionsGrid 函數，加入收藏按鈕
function updateAttractionsGrid(attractions) {
    const grid = document.querySelector('.attractions-grid');
    if (!grid) return;
    
    // 清空現有內容
    grid.innerHTML = '';
    
    if (attractions.length === 0) {
        grid.innerHTML = '<div class="no-results">未找到符合條件的景點</div>';
        return;
    }
    
    // 查看景點詳情函數
    function viewAttractionDetail(attractionId) {
        window.location.href = `/attraction/${attractionId}/`;
    }

    // 預設圖片映射
    const defaultImages = {
        '寺廟神社': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=300&h=180&fit=crop',
        '現代景點': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=300&h=180&fit=crop',
        '自然風光': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=300&h=180&fit=crop',
        '美食': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=300&h=180&fit=crop',
        '購物娛樂': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=180&fit=crop',
        'default': 'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=300&h=180&fit=crop'
    };
    
    attractions.forEach(attraction => {
        const card = document.createElement('div');
        card.className = 'attraction-card';
        card.onclick = () => viewAttractionDetail(attraction.id);
        
        // 選擇預設圖片
        let defaultImg = defaultImages['default'];
        if (attraction.type && defaultImages[attraction.type]) {
            defaultImg = defaultImages[attraction.type];
        }
        
        // 確定收藏狀態
        const favoriteIcon = attraction.is_favorited ? '❤️' : '🤍';
        const favoriteClass = attraction.is_favorited ? 'favorited' : '';
        const favoriteColor = attraction.is_favorited ? '#ff1744' : '#999';
        
        card.innerHTML = `
            <div class="attraction-image-container">
                <img src="${attraction.image || defaultImg}" 
                     alt="${attraction.name}" 
                     class="attraction-image"
                     onerror="this.src='${defaultImg}'">
                <button class="favorite-btn ${favoriteClass}" 
                        onclick="toggleFavorite(${attraction.id}, this)"
                        style="color: ${favoriteColor}">
                    ${favoriteIcon}
                </button>
            </div>
            <div class="attraction-info">
                <div class="attraction-name">${attraction.name}</div>
                <div class="attraction-location">${attraction.location}</div>
                <div class="attraction-rating">${attraction.rating_stars} ${attraction.rating}</div>
                <button class="view-detail-btn" onclick="event.stopPropagation(); viewAttractionDetail(${attraction.id})">查看詳情</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

// 為收藏頁面生成景點卡片
function generateFavoriteCard(attraction) {
    const defaultImages = {
        '寺廟神社': 'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=300&h=180&fit=crop',
        '現代景點': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=300&h=180&fit=crop',
        '自然風光': 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=300&h=180&fit=crop',
        '美食': 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=300&h=180&fit=crop',
        '購物娛樂': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=180&fit=crop',
        'default': 'https://images.unsplash.com/photo-1480796927426-f609979314bd?w=300&h=180&fit=crop'
    };
    
    let defaultImg = defaultImages['default'];
    if (attraction.type && defaultImages[attraction.type]) {
        defaultImg = defaultImages[attraction.type];
    }
    
    return `
        <div class="favorite-card" onclick="navigateToAttractionFromFavorites(${attraction.id})">
            <div class="attraction-image-container">
                <img src="${attraction.image || defaultImg}" 
                     alt="${attraction.name}" 
                     class="attraction-image"
                     onerror="this.src='${defaultImg}'">
                <button class="remove-favorite-btn" 
                        onclick="removeFromFavorites(${attraction.id}, this)"
                        title="從收藏中移除">
                    ✕
                </button>
            </div>
            <div class="attraction-info">
                <div class="attraction-name">${attraction.name}</div>
                <div class="attraction-location">${attraction.location}</div>
                <div class="attraction-rating">${attraction.rating_stars} ${attraction.rating}</div>
                <div class="favorite-actions">
                    <button class="view-detail-btn" onclick="event.stopPropagation(); navigateToAttractionFromFavorites(${attraction.id})">查看詳情</button>
                    <button class="add-to-plan-btn" onclick="event.stopPropagation(); showAddToPlanModal(${attraction.id})" data-attraction-id="${attraction.id}">加入行程</button>
                </div>
            </div>
        </div>
    `;
}

// 顯示加入行程的模態框
function showAddToPlanModal(attractionId) {
    // 如果已有模態框存在，先移除
    const existingModal = document.querySelector('.add-to-plan-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 創建模態框
    const modal = document.createElement('div');
    modal.className = 'add-to-plan-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>加入行程</h3>
                <button class="close-modal" onclick="closeAddToPlanModal()">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="modal-trip-select">選擇行程：</label>
                    <select id="modal-trip-select" class="form-control">
                        <option value="">請選擇行程...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="modal-date-select">選擇日期：</label>
                    <select id="modal-date-select" class="form-control">
                        <option value="">請先選擇行程...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="modal-remember-trip"> 記住我的選擇
                    </label>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeAddToPlanModal()">取消</button>
                <button class="btn-primary" onclick="addToTripFromModal(${attractionId})">加入行程</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 載入用戶的行程列表
    loadUserTripsForModal();
    
    // 點擊背景關閉模態框
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeAddToPlanModal();
        }
    });
}

// 關閉加入行程模態框
function closeAddToPlanModal() {
    const modal = document.querySelector('.add-to-plan-modal');
    if (modal) {
        modal.remove();
    }
}

// 載入用戶行程到模態框
function loadUserTripsForModal() {
    fetch('/get-user-trips/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tripSelect = document.getElementById('modal-trip-select');
                tripSelect.innerHTML = '<option value="">請選擇行程...</option>';
                
                data.trips.forEach(trip => {
                    const option = document.createElement('option');
                    option.value = trip.id;
                    option.textContent = trip.title;
                    tripSelect.appendChild(option);
                });
                
                // 綁定行程選擇變更事件
                tripSelect.addEventListener('change', function() {
                    loadTripDatesForModal(this.value);
                });
            }
        })
        .catch(error => {
            console.error('載入行程失敗:', error);
        });
}

// 載入行程日期到模態框
function loadTripDatesForModal(tripId) {
    const dateSelect = document.getElementById('modal-date-select');
    
    if (!tripId) {
        dateSelect.innerHTML = '<option value="">請先選擇行程...</option>';
        return;
    }
    
    fetch(`/get-trip-dates/${tripId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                dateSelect.innerHTML = '<option value="">請選擇日期...</option>';
                
                data.dates.forEach(date => {
                    const option = document.createElement('option');
                    option.value = date.date;
                    option.textContent = `第${date.day}天 (${date.date})`;
                    dateSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('載入日期失敗:', error);
        });
}

// 從模態框加入行程
function addToTripFromModal(attractionId) {
    const tripId = document.getElementById('modal-trip-select').value;
    const selectedDate = document.getElementById('modal-date-select').value;
    const rememberChoice = document.getElementById('modal-remember-trip').checked;
    
    if (!tripId || !selectedDate) {
        alert('請選擇行程和日期');
        return;
    }
    
    // 創建一個臨時按鈕對象來重用現有的 addToTrip 函數
    const tempButton = {
        getAttribute: () => attractionId,
        disabled: false,
        textContent: '加入中...',
        style: { background: '' }
    };
    
    // 更新模態框中的選擇到頁面元素（如果存在）
    const tripSelect = document.getElementById('trip-select');
    const dateSelectEl = document.getElementById('date-select');
    const rememberEl = document.getElementById('remember-trip');
    
    if (tripSelect) tripSelect.value = tripId;
    if (dateSelectEl) dateSelectEl.value = selectedDate;
    if (rememberEl) rememberEl.checked = rememberChoice;
    
    // 關閉模態框
    closeAddToPlanModal();
    
    // 調用現有的 addToTrip 函數
    addToTrip(tempButton);
}

// ========== CSS 樣式（需要加入到 CSS 文件中）==========

.attraction-image-container {
    position: relative;
}

.favorite-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.9);
    border: none;
    border-radius: 50%;
    width: 35px;
    height: 35px;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.favorite-btn:hover {
    background: rgba(255, 255, 255, 1);
    transform: scale(1.1);
}

.favorite-btn.favorited {
    background: rgba(255, 23, 68, 0.1);
}

.remove-favorite-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 0, 0, 0.8);
    color: white;
    border: none;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.remove-favorite-btn:hover {
    background: rgba(255, 0, 0, 1);
    transform: scale(1.1);
}

.favorite-card {
    cursor: pointer;
    transition: transform 0.3s ease;
}

.favorite-card:hover {
    transform: translateY(-5px);
}

.favorite-actions {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}

.favorite-actions button {
    flex: 1;
    padding: 8px 12px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
}

.view-detail-btn {
    background: #ff69b4;
    color: white;
}

.add-to-plan-btn {
    background: #28a745;
    color: white;
}

.empty-favorites {
    text-align: center;
    padding: 60px 20px;
    color: #666;
}

.empty-icon {
    font-size: 4em;
    margin-bottom: 20px;
}

.add-to-plan-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 10px;
    padding: 0;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #eee;
}

.close-modal {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
}

.modal-body {
    padding: 20px;
}

.modal-footer {
    display: flex;
    gap: 10px;
    padding: 20px;
    border-top: 1px solid #eee;
    justify-content: flex-end;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-control {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
}

.btn-primary, .btn-secondary {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
}

.btn-primary {
    background: #ff69b4;
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

