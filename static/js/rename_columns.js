        // Auto-select text when clicking on input fields
        document.querySelectorAll('.rename-input').forEach(input => {
            input.addEventListener('focus', function() {
                this.select();
            });
        });
        
        // Add validation to prevent empty submissions
        document.querySelector('form').addEventListener('submit', function(e) {
            const inputs = document.querySelectorAll('.rename-input');
            let hasValidInput = false;
            
            inputs.forEach(input => {
                if (input.value.trim() !== '') {
                    hasValidInput = true;
                }
            });
            
            if (!hasValidInput) {
                alert('Please provide at least one column name.');
                e.preventDefault();
            }
        });