
        // Chart download functionality
        function downloadChart(columnName, base64Image) {
            const link = document.createElement('a');
            link.download = `${columnName}_chart.png`;
            link.href = `data:image/png;base64,${base64Image}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        // Download all charts
        function downloadAllCharts() {
            const charts = document.querySelectorAll('.chart-card');
            charts.forEach((chart, index) => {
                setTimeout(() => {
                    const columnName = chart.dataset.column;
                    const img = chart.querySelector('.chart-image');
                    const base64 = img.src.split(',')[1];
                    downloadChart(columnName, base64);
                }, index * 200); // Stagger downloads
            });
        }

        function toggleChart(idx) {
            const img = document.getElementById('img-' + idx);
            const label = document.getElementById('label-' + idx);
            const column = img.closest('.chart-card').dataset.column;

            if (img.dataset.type === 'bar') {
                img.src = img.dataset.pie;
                img.dataset.type = 'pie';
                label.textContent = 'Pie Chart';
                updateSelectedGraphType(column, 'pie');
            } else {
                img.src = img.dataset.bar;
                img.dataset.type = 'bar';
                label.textContent = 'Bar Chart';
                updateSelectedGraphType(column, 'bar');
            }
        }

        function updateSelectedGraphType(column, graphType) {
            fetch('/update_selected_graph_type', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}' // Ensure CSRF token is included for Flask
                },
                body: JSON.stringify({ column: column, graphType: graphType })
            }).then(response => {
                if (!response.ok) {
                    console.error('Failed to update selected graph type');
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        }

        // Lazy loading animation
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.chart-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'all 0.5s ease';
                    
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 50);
                }, index * 100);
            });
        });

        // Image loading error handling
        document.querySelectorAll('.chart-image').forEach(img => {
            img.addEventListener('error', function() {
                this.parentElement.innerHTML = `
                    <div style="padding: 40px; color: #6c757d; text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">⚠️</div>
                        <p>Failed to load chart</p>
                    </div>
                `;
            });
        });

        // Add smooth scrolling
        document.documentElement.style.scrollBehavior = 'smooth';
