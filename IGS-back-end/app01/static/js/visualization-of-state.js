// 初始化菜单交互
document.addEventListener('DOMContentLoaded', function() {
    // 菜单点击事件
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        const menuTitle = item.querySelector('.menu-title');
        menuTitle.addEventListener('click', function() {
            item.classList.toggle('active');
        });
    });

    // 退出按钮事件
    const logoutBtn = document.querySelector('.logout-btn');
    logoutBtn.addEventListener('click', function() {
        alert('您已退出系统');
    });

    // 初始化知识掌握度图表
    const knowledgeCtx = document.getElementById('knowledgeChart').getContext('2d');
    const knowledgeChart = new Chart(knowledgeCtx, {
        type: 'radar',
        data: {
            labels: ['HTML', 'CSS', 'JavaScript', '数据库', '算法', '网络'],
            datasets: [{
                label: '掌握程度',
                data: [85, 75, 65, 60, 50, 70],
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(52, 152, 219, 1)'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });

    // 初始化学习进度图表
    const progressCtx = document.getElementById('progressChart').getContext('2d');
    const progressChart = new Chart(progressCtx, {
        type: 'bar',
        data: {
            labels: ['1月', '2月', '3月', '4月', '5月'],
            datasets: [{
                label: '学习时长(小时)',
                data: [30, 45, 60, 50, 40],
                backgroundColor: 'rgba(46, 204, 113, 0.6)',
                borderColor: 'rgba(46, 204, 113, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
