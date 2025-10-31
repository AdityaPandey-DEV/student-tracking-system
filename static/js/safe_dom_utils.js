/**
 * Safe DOM Utilities for student tracking system
 * Provides secure alternatives to innerHTML for XSS prevention
 */

class SafeDOM {
    
    /**
     * Safely create and set loading spinner
     * @param {HTMLElement} container - Container element
     */
    static showLoading(container) {
        container.textContent = ''; // Clear existing content
        
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'text-center';
        
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border';
        spinner.setAttribute('role', 'status');
        
        const spinnerText = document.createElement('span');
        spinnerText.className = 'visually-hidden';
        spinnerText.textContent = 'Loading...';
        
        spinner.appendChild(spinnerText);
        loadingDiv.appendChild(spinner);
        container.appendChild(loadingDiv);
    }
    
    /**
     * Safely create error message
     * @param {HTMLElement} container - Container element
     * @param {string} message - Error message (will be sanitized)
     */
    static showError(container, message) {
        container.textContent = ''; // Clear existing content
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-exclamation-circle me-2';
        
        const messageSpan = document.createElement('span');
        messageSpan.textContent = this.sanitizeText(message);
        
        alertDiv.appendChild(icon);
        alertDiv.appendChild(messageSpan);
        container.appendChild(alertDiv);
    }
    
    /**
     * Safely create teacher details card
     * @param {HTMLElement} container - Container element
     * @param {Object} teacher - Teacher data object
     */
    static createTeacherDetailsCard(container, teacher) {
        container.textContent = ''; // Clear existing content
        
        const card = document.createElement('div');
        card.className = 'card';
        
        // Card header
        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header bg-success text-white';
        
        const headerTitle = document.createElement('h5');
        headerTitle.className = 'mb-0';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-chalkboard-teacher me-2';
        
        const titleText = document.createElement('span');
        titleText.textContent = this.sanitizeText(teacher.name);
        
        headerTitle.appendChild(icon);
        headerTitle.appendChild(titleText);
        cardHeader.appendChild(headerTitle);
        
        // Card body
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        const row = document.createElement('div');
        row.className = 'row';
        
        // Left column
        const leftCol = document.createElement('div');
        leftCol.className = 'col-md-6';
        
        this.appendDetailField(leftCol, 'Employee ID', teacher.employee_id);
        this.appendDetailField(leftCol, 'Department', teacher.department || 'Not specified');
        this.appendDetailField(leftCol, 'Designation', teacher.designation || 'Not specified');
        this.appendDetailField(leftCol, 'Email', teacher.email);
        
        // Right column
        const rightCol = document.createElement('div');
        rightCol.className = 'col-md-6';
        
        this.appendDetailField(rightCol, 'Phone', teacher.phone_number || 'Not provided');
        this.appendDetailField(rightCol, 'Specialization', teacher.specialization || 'Not specified');
        this.appendDetailField(rightCol, 'Join Date', new Date(teacher.created_at).toLocaleDateString());
        
        // Status field with badge
        const statusP = document.createElement('p');
        const statusLabel = document.createElement('strong');
        statusLabel.textContent = 'Status: ';
        
        const statusBadge = document.createElement('span');
        statusBadge.className = `badge ${teacher.is_active ? 'bg-success' : 'bg-danger'}`;
        statusBadge.textContent = teacher.is_active ? 'Active' : 'Inactive';
        
        statusP.appendChild(statusLabel);
        statusP.appendChild(statusBadge);
        rightCol.appendChild(statusP);
        
        row.appendChild(leftCol);
        row.appendChild(rightCol);
        cardBody.appendChild(row);
        
        // Subjects section
        const hr = document.createElement('hr');
        cardBody.appendChild(hr);
        
        const subjectsTitle = document.createElement('h6');
        const subjectsIcon = document.createElement('i');
        subjectsIcon.className = 'fas fa-book me-2';
        subjectsTitle.appendChild(subjectsIcon);
        subjectsTitle.appendChild(document.createTextNode('Assigned Subjects'));
        cardBody.appendChild(subjectsTitle);
        
        const subjectsRow = document.createElement('div');
        subjectsRow.className = 'row';
        
        if (teacher.subjects && teacher.subjects.length > 0) {
            teacher.subjects.forEach(subject => {
                const subjectCol = document.createElement('div');
                subjectCol.className = 'col-md-4 mb-2';
                
                const subjectCard = document.createElement('div');
                subjectCard.className = 'card card-body';
                
                const subjectCode = document.createElement('strong');
                subjectCode.textContent = this.sanitizeText(subject.code);
                
                const subjectName = document.createElement('small');
                subjectName.className = 'text-muted';
                subjectName.textContent = this.sanitizeText(subject.name);
                
                const subjectCourse = document.createElement('small');
                subjectCourse.className = 'text-info';
                subjectCourse.textContent = `${this.sanitizeText(subject.course)} - Year ${subject.year}`;
                
                subjectCard.appendChild(subjectCode);
                subjectCard.appendChild(document.createElement('br'));
                subjectCard.appendChild(subjectName);
                subjectCard.appendChild(document.createElement('br'));
                subjectCard.appendChild(subjectCourse);
                
                subjectCol.appendChild(subjectCard);
                subjectsRow.appendChild(subjectCol);
            });
        } else {
            const noSubjects = document.createElement('p');
            noSubjects.className = 'text-muted';
            noSubjects.textContent = 'No subjects assigned';
            subjectsRow.appendChild(noSubjects);
        }
        
        cardBody.appendChild(subjectsRow);
        
        // Card footer with buttons
        const cardFooter = document.createElement('div');
        cardFooter.className = 'card-footer';
        
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-warning btn-sm';
        editBtn.onclick = () => editTeacher(teacher.id);
        
        const editIcon = document.createElement('i');
        editIcon.className = 'fas fa-edit me-1';
        editBtn.appendChild(editIcon);
        editBtn.appendChild(document.createTextNode('Edit Details'));
        
        const scheduleBtn = document.createElement('button');
        scheduleBtn.className = 'btn btn-info btn-sm';
        scheduleBtn.onclick = () => viewTeacherSchedule(teacher.id);
        
        const scheduleIcon = document.createElement('i');
        scheduleIcon.className = 'fas fa-calendar me-1';
        scheduleBtn.appendChild(scheduleIcon);
        scheduleBtn.appendChild(document.createTextNode('View Schedule'));
        
        cardFooter.appendChild(editBtn);
        cardFooter.appendChild(scheduleBtn);
        
        // Assemble card
        card.appendChild(cardHeader);
        card.appendChild(cardBody);
        card.appendChild(cardFooter);
        
        container.appendChild(card);
    }
    
    /**
     * Helper function to append detail field
     * @param {HTMLElement} parent - Parent element
     * @param {string} label - Field label
     * @param {string} value - Field value
     */
    static appendDetailField(parent, label, value) {
        const p = document.createElement('p');
        const strong = document.createElement('strong');
        strong.textContent = label + ': ';
        p.appendChild(strong);
        p.appendChild(document.createTextNode(this.sanitizeText(value)));
        parent.appendChild(p);
    }
    
    /**
     * Sanitize text content to prevent XSS
     * @param {string} text - Text to sanitize
     * @returns {string} - Sanitized text
     */
    static sanitizeText(text) {
        if (!text) return '';
        return String(text).replace(/[<>&'"]/g, function(char) {
            switch(char) {
                case '<': return '&lt;';
                case '>': return '&gt;';
                case '&': return '&amp;';
                case '"': return '&quot;';
                case "'": return '&#x27;';
                default: return char;
            }
        });
    }
    
    /**
     * Create CSRF token input for forms
     * @returns {HTMLInputElement} - CSRF token input
     */
    static createCSRFInput() {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return input;
    }
    
    /**
     * Safely create a form field
     * @param {string} type - Input type
     * @param {string} name - Field name
     * @param {string} label - Field label
     * @param {string} value - Field value
     * @param {boolean} required - Whether field is required
     * @returns {HTMLElement} - Form field container
     */
    static createFormField(type, name, label, value = '', required = false) {
        const container = document.createElement('div');
        container.className = 'mb-3';
        
        const labelElement = document.createElement('label');
        labelElement.className = 'form-label';
        labelElement.textContent = label;
        labelElement.setAttribute('for', name);
        
        let inputElement;
        if (type === 'textarea') {
            inputElement = document.createElement('textarea');
            inputElement.rows = 3;
            inputElement.textContent = this.sanitizeText(value);
        } else {
            inputElement = document.createElement('input');
            inputElement.type = type;
            inputElement.value = this.sanitizeText(value);
        }
        
        inputElement.className = 'form-control';
        inputElement.name = name;
        inputElement.id = name;
        
        if (required) {
            inputElement.required = true;
        }
        
        container.appendChild(labelElement);
        container.appendChild(inputElement);
        
        return container;
    }
}

// Export for use in other files
window.SafeDOM = SafeDOM;
