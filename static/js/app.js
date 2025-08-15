// Main application JavaScript
class WallpaperManager {
    constructor() {
        this.wallpapers = {
            subscribed: [],
            unsubscribed: []
        };
        this.selectedWallpapers = new Set();
        this.currentWallpaper = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadConfiguration();
        this.loadData();
    }
    
    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterWallpapers(e.target.value);
            });
        }
        
        // Status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filterByStatus(e.target.value);
            });
        }
        
        // Select all checkbox
        const selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }
        
        // Tab change events
        const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabLinks.forEach(tab => {
            tab.addEventListener('shown.bs.tab', () => {
                this.updateSelectAllState();
            });
        });
    }
    
    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            const result = await response.json();
            
            if (result.success) {
                this.populateConfigForm(result.data);
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
    }
    
    populateConfigForm(config) {
        const steamLibraryPath = document.getElementById('steamLibraryPath');
        const serverPort = document.getElementById('serverPort');
        const debugMode = document.getElementById('debugMode');
        
        if (steamLibraryPath) steamLibraryPath.value = config.steam_library_path || '';
        if (serverPort) serverPort.value = config.server?.port || 5000;
        if (debugMode) debugMode.checked = config.server?.debug || false;
    }
    
    async loadData() {
        this.showLoading(true);
        
        try {
            // Load wallpapers
            const wallpaperResponse = await fetch('/api/wallpapers');
            const wallpaperResult = await wallpaperResponse.json();
            
            if (wallpaperResult.success) {
                this.wallpapers.subscribed = wallpaperResult.data.subscribed || [];
                this.wallpapers.unsubscribed = wallpaperResult.data.unsubscribed || [];
                this.renderWallpapers();
            } else {
                this.showToast('Error loading wallpapers: ' + wallpaperResult.error, 'error');
            }
            
            // Load statistics
            const statsResponse = await fetch('/api/stats');
            const statsResult = await statsResponse.json();
            
            if (statsResult.success) {
                this.updateStatistics(statsResult.data);
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showToast('Error loading data: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    updateStatistics(stats) {
        document.getElementById('totalCount').textContent = stats.total.count;
        document.getElementById('totalSize').textContent = stats.total.size_formatted;
        
        document.getElementById('subscribedCount').textContent = stats.subscribed.count;
        document.getElementById('subscribedSize').textContent = stats.subscribed.size_formatted;
        
        document.getElementById('unsubscribedCount').textContent = stats.unsubscribed.count;
        document.getElementById('unsubscribedSize').textContent = stats.unsubscribed.size_formatted;
        
        document.getElementById('reclaimableSize').textContent = stats.unsubscribed.size_formatted;
        
        // Update badges
        document.getElementById('subscribedBadge').textContent = stats.subscribed.count;
        document.getElementById('unsubscribedBadge').textContent = stats.unsubscribed.count;
    }
    
    renderWallpapers() {
        this.renderWallpaperGrid('subscribedWallpapers', this.wallpapers.subscribed, false);
        this.renderWallpaperGrid('unsubscribedWallpapers', this.wallpapers.unsubscribed, true);
    }
    
    renderWallpaperGrid(containerId, wallpapers, showCheckbox = false) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (wallpapers.length === 0) {
            container.innerHTML = `
                <div class="empty-state col-12">
                    <i class="fas fa-images"></i>
                    <h5>没有找到壁纸</h5>
                    <p class="text-muted">当前分类下暂无壁纸数据</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = wallpapers.map(wallpaper => 
            this.createWallpaperCard(wallpaper, showCheckbox)
        ).join('');
        
        // Load preview images
        this.loadPreviewImages(container);
    }
    
    createWallpaperCard(wallpaper, showCheckbox = false) {
        const statusClass = wallpaper.subscribed ? 'status-subscribed' : 'status-unsubscribed';
        const statusText = wallpaper.subscribed ? '已订阅' : '未订阅';
        
        return `
            <div class="wallpaper-card" data-id="${wallpaper.id}" onclick="wallpaperManager.showWallpaperDetail('${wallpaper.id}')">
                ${showCheckbox ? `
                    <div class="wallpaper-checkbox">
                        <input type="checkbox" class="form-check-input" 
                               onclick="event.stopPropagation(); wallpaperManager.toggleWallpaperSelection('${wallpaper.id}', this.checked)">
                    </div>
                ` : ''}
                
                <div class="wallpaper-preview loading" data-id="${wallpaper.id}">
                    <i class="fas fa-image fa-2x"></i>
                </div>
                
                <div class="wallpaper-info">
                    <div class="wallpaper-title">${wallpaper.title}</div>
                    <div class="wallpaper-meta">
                        <span class="wallpaper-id">ID: ${wallpaper.id}</span>
                        <span class="wallpaper-size">${wallpaper.size_formatted}</span>
                    </div>
                    <div class="wallpaper-status">
                        <span class="badge ${statusClass}">${statusText}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    async loadPreviewImages(container) {
        const previewElements = container.querySelectorAll('.wallpaper-preview[data-id]');
        
        for (const element of previewElements) {
            const wallpaperId = element.dataset.id;
            try {
                const img = document.createElement('img');
                img.src = `/api/wallpapers/${wallpaperId}/preview`;
                img.alt = 'Preview';
                img.onerror = () => {
                    element.innerHTML = '<i class="fas fa-image-slash fa-2x"></i><br><small>无预览</small>';
                    element.classList.remove('loading');
                };
                img.onload = () => {
                    element.innerHTML = '';
                    element.appendChild(img);
                    element.classList.remove('loading');
                };
            } catch (error) {
                element.innerHTML = '<i class="fas fa-exclamation-triangle fa-2x"></i><br><small>加载失败</small>';
                element.classList.remove('loading');
            }
        }
    }
    
    toggleWallpaperSelection(wallpaperId, selected) {
        if (selected) {
            this.selectedWallpapers.add(wallpaperId);
        } else {
            this.selectedWallpapers.delete(wallpaperId);
        }
        
        this.updateSelectAllState();
    }
    
    toggleSelectAll(selectAll) {
        const activeTab = document.querySelector('.tab-pane.active');
        const checkboxes = activeTab.querySelectorAll('.wallpaper-checkbox input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAll;
            const wallpaperId = checkbox.closest('.wallpaper-card').dataset.id;
            this.toggleWallpaperSelection(wallpaperId, selectAll);
        });
    }
    
    updateSelectAllState() {
        const activeTab = document.querySelector('.tab-pane.active');
        const checkboxes = activeTab.querySelectorAll('.wallpaper-checkbox input[type="checkbox"]');
        const selectAllCheckbox = document.getElementById('selectAll');
        
        if (!selectAllCheckbox || checkboxes.length === 0) return;
        
        const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
        
        if (checkedCount === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (checkedCount === checkboxes.length) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
        }
    }
    
    async showWallpaperDetail(wallpaperId) {
        try {
            const response = await fetch(`/api/wallpapers/${wallpaperId}`);
            const result = await response.json();
            
            if (result.success) {
                this.currentWallpaper = result.data;
                this.populateDetailModal(result.data);
                
                const modal = new bootstrap.Modal(document.getElementById('wallpaperModal'));
                modal.show();
            } else {
                this.showToast('Error loading wallpaper details: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error loading wallpaper details:', error);
            this.showToast('Error loading wallpaper details: ' + error.message, 'error');
        }
    }
    
    populateDetailModal(wallpaper) {
        document.getElementById('wallpaperModalTitle').textContent = wallpaper.title;
        document.getElementById('wallpaperDetailId').textContent = wallpaper.id;
        document.getElementById('wallpaperDetailTitle').textContent = wallpaper.title;
        document.getElementById('wallpaperDetailSize').textContent = wallpaper.size_formatted;
        document.getElementById('wallpaperDetailStatus').innerHTML = 
            `<span class="badge ${wallpaper.subscribed ? 'status-subscribed' : 'status-unsubscribed'}">
                ${wallpaper.subscribed ? '已订阅' : '未订阅'}
            </span>`;
        
        // Display path with proper formatting
        const pathElement = document.getElementById('wallpaperDetailPath');
        pathElement.textContent = wallpaper.path;
        pathElement.title = wallpaper.path; // Show full path on hover
        
        // Load large preview
        const previewImg = document.getElementById('wallpaperPreviewLarge');
        previewImg.src = `/api/wallpapers/${wallpaper.id}/preview`;
        
        // Show/hide delete button based on subscription status
        const deleteButton = document.getElementById('deleteButton');
        if (deleteButton) {
            deleteButton.style.display = wallpaper.subscribed ? 'none' : 'inline-block';
        }
    }
    
    filterWallpapers(searchTerm) {
        const term = searchTerm.toLowerCase();
        const cards = document.querySelectorAll('.wallpaper-card');
        
        cards.forEach(card => {
            const title = card.querySelector('.wallpaper-title').textContent.toLowerCase();
            const id = card.dataset.id.toLowerCase();
            
            if (title.includes(term) || id.includes(term)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    filterByStatus(status) {
        const subscribedTab = document.getElementById('subscribed-tab');
        const unsubscribedTab = document.getElementById('unsubscribed-tab');
        
        switch (status) {
            case 'subscribed':
                subscribedTab.click();
                break;
            case 'unsubscribed':
                unsubscribedTab.click();
                break;
            case 'all':
            default:
                // Show all - keep current tab
                break;
        }
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.toggle('hidden', !show);
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        if (toast && toastMessage) {
            toastMessage.textContent = message;
            
            // Update toast header icon based on type
            const icon = toast.querySelector('.toast-header i');
            if (icon) {
                icon.className = `fas ${type === 'error' ? 'fa-exclamation-triangle text-danger' : 'fa-info-circle text-primary'} me-2`;
            }
            
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }
}

// Global functions
function refreshData() {
    if (window.wallpaperManager) {
        window.wallpaperManager.loadData();
    }
}

async function saveConfig() {
    // 获取表单数据并进行验证
    const steamLibraryPath = document.getElementById('steamLibraryPath')?.value || '';
    const serverPortInput = document.getElementById('serverPort');
    const debugModeInput = document.getElementById('debugMode');
    
    // 验证端口号
    const serverPort = serverPortInput ? parseInt(serverPortInput.value) : 5000;
    if (isNaN(serverPort) || serverPort < 1 || serverPort > 65535) {
        window.wallpaperManager.showToast('请输入有效的端口号 (1-65535)', 'error');
        return;
    }
    
    const debugMode = debugModeInput ? debugModeInput.checked : false;
    
    const config = {
        steam_library_path: steamLibraryPath,
        server: {
            host: '127.0.0.1',
            port: serverPort,
            debug: debugMode
        }
    };
    
    console.log('Sending config:', config); // Debug log
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        console.log('Response status:', response.status); // Debug log
        
        if (!response.ok) {
            console.error('HTTP error:', response.status, response.statusText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Response data:', result); // Debug log
        
        if (result.success) {
            window.wallpaperManager.showToast('配置保存成功', 'info');
            const modal = bootstrap.Modal.getInstance(document.getElementById('configModal'));
            if (modal) {
                modal.hide();
            }
            
            // Reload data with new configuration
            setTimeout(() => {
                refreshData();
            }, 500);
        } else {
            const errorMsg = result.error || result.message || '配置保存失败';
            console.error('Config save failed:', errorMsg);
            window.wallpaperManager.showToast('配置保存失败: ' + errorMsg, 'error');
        }
    } catch (error) {
        console.error('Config save error:', error);
        let errorMsg = '网络连接错误';
        if (error.message) {
            errorMsg = error.message;
        }
        window.wallpaperManager.showToast('配置保存失败: ' + errorMsg, 'error');
    }
}

async function deleteSelected() {
    if (!window.wallpaperManager.selectedWallpapers.size) {
        window.wallpaperManager.showToast('请先选择要删除的壁纸', 'error');
        return;
    }
    
    const count = window.wallpaperManager.selectedWallpapers.size;
    if (!confirm(`确定要删除选中的 ${count} 个壁纸吗？此操作不可撤销！`)) {
        return;
    }
    
    window.wallpaperManager.showLoading(true);
    
    let successCount = 0;
    for (const wallpaperId of window.wallpaperManager.selectedWallpapers) {
        try {
            const response = await fetch(`/api/wallpapers/${wallpaperId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.success) {
                successCount++;
            }
        } catch (error) {
            console.error('Error deleting wallpaper:', error);
        }
    }
    
    window.wallpaperManager.showLoading(false);
    window.wallpaperManager.showToast(`成功删除 ${successCount} 个壁纸`, 'info');
    window.wallpaperManager.selectedWallpapers.clear();
    refreshData();
}

async function deleteAll() {
    const count = window.wallpaperManager.wallpapers.unsubscribed.length;
    if (count === 0) {
        window.wallpaperManager.showToast('没有可删除的未订阅壁纸', 'info');
        return;
    }
    
    if (!confirm(`确定要删除所有 ${count} 个未订阅壁纸吗？此操作不可撤销！`)) {
        return;
    }
    
    window.wallpaperManager.showLoading(true);
    
    let successCount = 0;
    for (const wallpaper of window.wallpaperManager.wallpapers.unsubscribed) {
        try {
            const response = await fetch(`/api/wallpapers/${wallpaper.id}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.success) {
                successCount++;
            }
        } catch (error) {
            console.error('Error deleting wallpaper:', error);
        }
    }
    
    window.wallpaperManager.showLoading(false);
    window.wallpaperManager.showToast(`成功删除 ${successCount} 个壁纸`, 'info');
    refreshData();
}

async function deleteWallpaper() {
    if (!window.wallpaperManager.currentWallpaper) return;
    
    const wallpaper = window.wallpaperManager.currentWallpaper;
    if (!confirm(`确定要删除壁纸 "${wallpaper.title}" 吗？此操作不可撤销！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/wallpapers/${wallpaper.id}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result.success) {
            window.wallpaperManager.showToast('壁纸删除成功', 'info');
            const modal = bootstrap.Modal.getInstance(document.getElementById('wallpaperModal'));
            modal.hide();
            refreshData();
        } else {
            window.wallpaperManager.showToast('壁纸删除失败: ' + result.error, 'error');
        }
    } catch (error) {
        window.wallpaperManager.showToast('壁纸删除失败: ' + error.message, 'error');
    }
}

async function openFolder() {
    if (!window.wallpaperManager.currentWallpaper) {
        window.wallpaperManager.showToast('没有选中的壁纸', 'error');
        return;
    }
    
    const wallpaper = window.wallpaperManager.currentWallpaper;
    
    try {
        const response = await fetch(`/api/wallpapers/${wallpaper.id}/open-folder`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Error opening folder:', error);
        // Fallback: show path in toast
        window.wallpaperManager.showToast(`打开文件夹失败，路径: ${wallpaper.path}`, 'error');
    }
}

function copyPath() {
    if (!window.wallpaperManager.currentWallpaper) {
        window.wallpaperManager.showToast('没有选中的壁纸', 'error');
        return;
    }
    
    const path = window.wallpaperManager.currentWallpaper.path;
    
    // Try to copy to clipboard
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(path).then(() => {
            window.wallpaperManager.showToast('路径已复制到剪贴板', 'info');
        }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
            window.wallpaperManager.showToast(`路径: ${path}`, 'info');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = path;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            window.wallpaperManager.showToast('路径已复制到剪贴板', 'info');
        } catch (err) {
            window.wallpaperManager.showToast(`路径: ${path}`, 'info');
        }
        document.body.removeChild(textArea);
    }
}

function exportData(type) {
    const data = type === 'subscribed' ? 
        window.wallpaperManager.wallpapers.subscribed : 
        window.wallpaperManager.wallpapers.unsubscribed;
    
    if (data.length === 0) {
        window.wallpaperManager.showToast('没有数据可导出', 'info');
        return;
    }
    
    // Create CSV content
    const headers = ['ID', '标题', '大小', '状态', '路径'];
    const csvContent = [
        headers.join(','),
        ...data.map(wp => [
            wp.id,
            `"${wp.title.replace(/"/g, '""')}"`,
            wp.size_formatted,
            wp.subscribed ? '已订阅' : '未订阅',
            `"${wp.path.replace(/"/g, '""')}"`
        ].join(','))
    ].join('\n');
    
    // Download file
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `wallpapers_${type}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    window.wallpaperManager.showToast('数据导出成功', 'info');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.wallpaperManager = new WallpaperManager();
});
