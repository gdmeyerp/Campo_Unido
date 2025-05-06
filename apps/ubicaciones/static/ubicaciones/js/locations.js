// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to show loading state
function showLoading(selectElement) {
    selectElement.disabled = true;
    const loadingOption = document.createElement('option');
    loadingOption.value = '';
    loadingOption.textContent = 'Cargando...';
    selectElement.innerHTML = '';
    selectElement.appendChild(loadingOption);
}

// Function to show error state
function showError(selectElement, message) {
    selectElement.disabled = true;
    const errorOption = document.createElement('option');
    errorOption.value = '';
    errorOption.textContent = message || 'Error al cargar datos';
    selectElement.innerHTML = '';
    selectElement.appendChild(errorOption);
}

// Function to update cities dropdown based on selected state
function updateCities(stateId) {
    const citySelect = document.getElementById('id_ciudad');
    if (!citySelect) return;

    // Clear current options and disable
    citySelect.innerHTML = '<option value="">Seleccione una ciudad</option>';
    citySelect.disabled = !stateId;
    
    if (!stateId) return;

    // Show loading state
    showLoading(citySelect);

    // Get cities for selected state
    fetch(`/ubicaciones/api/ciudades/${stateId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar las ciudades');
            }
            return response.json();
        })
        .then(data => {
            citySelect.innerHTML = '<option value="">Todas las ciudades</option>';
            data.ciudades.forEach(city => {
                const option = document.createElement('option');
                option.value = city.id;
                option.textContent = city.nombre;
                citySelect.appendChild(option);
            });
            citySelect.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            showError(citySelect, 'Error al cargar las ciudades');
        });
}

// Function to update states dropdown based on selected country
function updateStates(countryId) {
    const stateSelect = document.getElementById('id_estado');
    const citySelect = document.getElementById('id_ciudad');
    if (!stateSelect) return;

    // Clear current options and disable
    stateSelect.innerHTML = '<option value="">Seleccione un estado</option>';
    stateSelect.disabled = !countryId;
    
    // Clear and disable cities
    if (citySelect) {
        citySelect.innerHTML = '<option value="">Seleccione una ciudad</option>';
        citySelect.disabled = true;
    }
    
    if (!countryId) return;

    // Show loading state
    showLoading(stateSelect);

    // Get states for selected country
    fetch(`/ubicaciones/api/estados/${countryId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar los estados');
            }
            return response.json();
        })
        .then(data => {
            stateSelect.innerHTML = '<option value="">Todos los estados</option>';
            data.estados.forEach(state => {
                const option = document.createElement('option');
                option.value = state.id;
                option.textContent = state.nombre;
                stateSelect.appendChild(option);
            });
            stateSelect.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            showError(stateSelect, 'Error al cargar los estados');
        });
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const countrySelect = document.getElementById('id_pais');
    const stateSelect = document.getElementById('id_estado');
    const citySelect = document.getElementById('id_ciudad');

    if (countrySelect) {
        countrySelect.addEventListener('change', function() {
            updateStates(this.value);
        });
    }

    if (stateSelect) {
        stateSelect.addEventListener('change', function() {
            updateCities(this.value);
        });
    }

    // Initialize states if country is selected
    if (countrySelect && countrySelect.value) {
        updateStates(countrySelect.value);
    }

    // Initialize cities if state is selected
    if (stateSelect && stateSelect.value) {
        updateCities(stateSelect.value);
    }
}); 