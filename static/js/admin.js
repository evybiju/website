// Tab switching functionality
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabPane = document.querySelector(`#${button.dataset.tab}`);
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        tabPane.classList.add('active');
    });
});

// Delete confirmation modal functionality
document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', () => {
        const id = button.dataset.id;
        const type = button.dataset.type;
        const modal = document.getElementById('deleteModal');
        const deleteForm = document.getElementById('deleteForm');
        const deleteItemId = document.getElementById('deleteItemId');
        deleteItemId.value = id;

        // Set form action dynamically based on type
        deleteForm.action = `/admin/delete_${type}/${id}`;
        
        modal.classList.remove('hidden');
    });
});

// Cancel delete action
document.getElementById('cancelDelete').addEventListener('click', () => {
    document.getElementById('deleteModal').classList.add('hidden');
});
