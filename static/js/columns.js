
        // Optional: Add select all functionality
        function addSelectAllButton() {
            const form = document.querySelector('form');
            const selectAllBtn = document.createElement('button');
            selectAllBtn.type = 'button';
            selectAllBtn.textContent = 'Select All';
            selectAllBtn.style.marginRight = '10px';
            selectAllBtn.onclick = function() {
                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                checkboxes.forEach(cb => cb.checked = !allChecked);
                this.textContent = allChecked ? 'Select All' : 'Deselect All';
            };
            
            const submitBtn = document.querySelector('.submit-btn');
            submitBtn.parentNode.insertBefore(selectAllBtn, submitBtn);
        }
        
        addSelectAllButton();