document.addEventListener('DOMContentLoaded', function() {
    // Get the table element
    const invoiceTable = document.getElementById('invoice-table');
    const sortLinks = document.querySelectorAll('.sort-link');
    
    // Add click event to sort links
    sortLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sortBy = this.dataset.sort;
            
            // Show loading indicator
            document.getElementById('loading-indicator').style.display = 'block';
            
            // Fetch sorted data via AJAX
            fetch(`/invoices/?sort=${sortBy}&format=json`)
                .then(response => response.json())
                .then(data => {
                    updateInvoiceTable(data.invoices);
                    document.getElementById('loading-indicator').style.display = 'none';
                })
                .catch(error => {
                    console.error('Error fetching sorted invoices:', error);
                    document.getElementById('loading-indicator').style.display = 'none';
                });
        });
    });
    
    // Add filter functionality
    const statusFilter = document.getElementById('status-filter');
    statusFilter.addEventListener('change', function() {
        const status = this.value;
        
        // Show loading indicator
        document.getElementById('loading-indicator').style.display = 'block';
        
        // Fetch filtered data
        fetch(`/invoices/?status=${status}&format=json`)
            .then(response => response.json())
            .then(data => {
                updateInvoiceTable(data.invoices);
                document.getElementById('loading-indicator').style.display = 'none';
            })
            .catch(error => {
                console.error('Error fetching filtered invoices:', error);
                document.getElementById('loading-indicator').style.display = 'none';
            });
    });
    
    // Add search functionality
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function performSearch() {
        const searchTerm = searchInput.value.trim();
        if (!searchTerm) return;
        
        // Show loading indicator
        document.getElementById('loading-indicator').style.display = 'block';
        
        // Get current status filter value
        const statusFilter = document.getElementById('status-filter').value;
        
        // Fetch search results
        fetch(`/invoices/?search=${searchTerm}&status=${statusFilter}&format=json`)
            .then(response => response.json())
            .then(data => {
                updateInvoiceTable(data.invoices);
                document.getElementById('loading-indicator').style.display = 'none';
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
                document.getElementById('loading-indicator').style.display = 'none';
            });
    }
    
    // Function to update the table with new data
    function updateInvoiceTable(invoices) {
        const tableBody = invoiceTable.querySelector('tbody');
        tableBody.innerHTML = '';
        
        invoices.forEach(invoice => {
            const row = document.createElement('tr');
            row.className = invoice.status === 'overdue' ? 'table-danger' : 
                           invoice.status === 'paid' ? 'table-success' : '';
            
            row.innerHTML = `
                <td>${invoice.client_name}</td>
                <td><a href="/invoices/${invoice.id}/">${invoice.id}</a></td>
                <td>${invoice.sum}</td>
                <td>${invoice.status_display}</td>
                <td>${invoice.payment_date}</td>
                <td>
                    ${invoice.status !== 'paid' ? 
                    `<input type="checkbox" name="invoice_ids" value="${invoice.id}">` : 
                    '<span>Paid</span>'}
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    }
}); 