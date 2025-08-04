let currentEditingJobId = null;
let dashboardData = {};
let nextJobIndices = {}; // Track current index of next job per machine

// Digital Clock
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('id-ID', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('digital-clock').textContent = timeString;
}

// Initialize clock
setInterval(updateClock, 1000);
updateClock();

// Load dashboard data
async function loadDashboardData() {
    try {
        const response = await fetch('/dashboard_data');
        dashboardData = await response.json();

        // Initialize nextJobIndices for machines if not set
        for (const machine in dashboardData) {
            if (!(machine in nextJobIndices)) {
                nextJobIndices[machine] = 0;
            }
        }

        renderDashboard();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error loading dashboard data', 'error');
    }
}

// Render dashboard
function renderDashboard() {
    const grid = document.getElementById('dashboard-grid');
    const machines = ['CNC1', 'CNC2', 'CNC3', 'CNC4', 'CNC5'];
    
    grid.innerHTML = machines.map(machine => {
        const machineData = dashboardData[machine] || { current: null, next_jobs: [], total_jobs: 0 };
        return createMachineCard(machine, machineData);
    }).join('');
}

// Create machine card
function createMachineCard(machine, data) {
    const currentJob = data.current;
    const nextJobs = data.next_jobs || [];
    const totalJobs = data.total_jobs || 0;

    // Use current index for next job
    let nextJobIndex = nextJobIndices[machine] || 0;
    if (nextJobIndex >= nextJobs.length) {
        nextJobIndex = 0;
        nextJobIndices[machine] = 0;
    }
    const nextJob = nextJobs.length > 0 ? nextJobs[nextJobIndex] : null;
    
    return `
        <div class="bg-slate-800/50 rounded-xl p-6 card-glow slide-in">
            <!-- Machine Header -->
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold orbitron text-cyan-400">${machine}</h3>
                <span class="bg-cyan-600/20 text-cyan-400 px-3 py-1 rounded-full text-sm font-semibold">
                    ${totalJobs} Jobs
                </span>
            </div>
            
            <!-- Current Job -->
            <div class="mb-6">
                <h4 class="text-sm font-semibold text-green-400 mb-2 flex items-center">
                    <span class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
                    CURRENT JOB
                </h4>
                ${currentJob ? createJobCard(currentJob, 'current') : createEmptyJobCard('current')}
            </div>
            
            <!-- Next Job -->
            <div>
                <div class="flex justify-between items-center mb-2">
                    <h4 class="text-sm font-semibold text-blue-400 flex items-center">
                        <span class="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                        NEXT JOB
                    </h4>
                    ${nextJobs.length > 1 ? `
                        <div class="flex space-x-1">
                            <button onclick="navigateJob('${machine}', 'prev')" class="text-xs bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded">‹</button>
                            <span class="text-xs text-gray-400">${nextJobIndex + 1}/${nextJobs.length}</span>
                            <button onclick="navigateJob('${machine}', 'next')" class="text-xs bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded">›</button>
                        </div>
                    ` : ''}
                </div>
                ${nextJob ? createJobCard(nextJob, 'next') : createEmptyJobCard('next')}
            </div>
        </div>
    `;
}

// Create job card
function createJobCard(job, type) {
    const progressColor = job.ACHIEVEMENT >= 80 ? 'green' : job.ACHIEVEMENT >= 60 ? 'yellow' : 'red';
    
    return `
        <div class="bg-slate-700/50 rounded-lg p-4 border border-slate-600/50">
            <div class="flex justify-between items-start mb-3">
                <div>
                    <h5 class="font-semibold text-white">${job.MODEL}</h5>
                    <p class="text-sm text-gray-300">${job.PART} - ${job.SIZE}</p>
                </div>
                <div class="flex space-x-1">
                    <button onclick="editJob(${job.id})" class="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded transition-colors">
                        ✏️
                    </button>
                    ${type === 'current' ? `
                        <button onclick="finishJob(${job.id})" class="text-xs bg-green-600 hover:bg-green-700 px-2 py-1 rounded transition-colors">
                            ✓
                        </button>
                    ` : ''}
                </div>
            </div>
            
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span class="text-gray-400">Start:</span>
                    <span class="text-white">${job.START || '-'}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">Finish:</span>
                    <span class="text-white">${job.FINISH || '-'}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">Target:</span>
                    <span class="text-white">${job.ETC_H}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">Operator:</span>
                    <span class="text-white">${job.OPERATOR}</span>
                </div>
            </div>
            
            <!-- Progress Bar -->
            <div class="mt-3">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-xs text-gray-400">Achievement</span>
                    <span class="text-xs font-semibold text-${progressColor}-400">${job.ACHIEVEMENT.toFixed(1)}%</span>
                </div>
                <div class="w-full bg-slate-600 rounded-full h-2">
                    <div class="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-2 rounded-full progress-glow transition-all duration-500" 
                         style="width: ${job.ACHIEVEMENT}%"></div>
                </div>
            
            </div>
            
            ${job.REMARK ? `
                <div class="mt-2 p-2 bg-slate-800/50 rounded text-xs text-gray-300">
                    <strong>Remark:</strong> ${job.REMARK}
                </div>
            ` : ''}
        </div>
    `;
}

// Create empty job card
function createEmptyJobCard(type) {
    return `
        <div class="bg-slate-700/30 rounded-lg p-4 border border-dashed border-slate-600/50 text-center">
            <div class="text-gray-500 text-sm">
                <div class="text-2xl mb-2">📋</div>
                <p>No ${type} job</p>
            </div>
        </div>
    `;
}

// Modal functions
function openAddModal() {
    document.getElementById('modal-title').textContent = 'Tambah Job Baru';
    document.getElementById('job-id').value = '';
    document.getElementById('job-form').reset();
    currentEditingJobId = null;
    document.getElementById('job-modal').classList.remove('hidden');
    document.getElementById('job-modal').classList.add('flex');
}

function closeModal() {
    document.getElementById('job-modal').classList.add('hidden');
    document.getElementById('job-modal').classList.remove('flex');
    currentEditingJobId = null;
}

// Edit job
async function editJob(jobId) {
    try {
        const response = await fetch(`/job_data/${jobId}`);
        const jobData = await response.json();
        
        if (jobData.error) {
            showAlert('Error loading job data', 'error');
            return;
        }
        
        // Fill form with job data
        document.getElementById('modal-title').textContent = 'Edit Job';
        document.getElementById('job-id').value = jobId;
        document.getElementById('mesin').value = jobData.mesin;
        document.querySelector(`input[name="job_type"][value="${jobData.job_type}"]`).checked = true;
        document.getElementById('MODEL').value = jobData.MODEL;
        document.getElementById('PART').value = jobData.PART;
        document.getElementById('SIZE').value = jobData.SIZE;
        document.getElementById('ETC_H').value = jobData.ETC_H;
        document.getElementById('OPERATOR').value = jobData.OPERATOR;
        document.getElementById('REMARK').value = jobData.REMARK || '';
        
        // Convert datetime format for input fields
        if (jobData.START) {
            document.getElementById('START').value = convertToDatetimeLocal(jobData.START);
        }
        if (jobData.FINISH) {
            document.getElementById('FINISH').value = convertToDatetimeLocal(jobData.FINISH);
        }
        
        currentEditingJobId = jobId;
        document.getElementById('job-modal').classList.remove('hidden');
        document.getElementById('job-modal').classList.add('flex');
        
    } catch (error) {
        console.error('Error loading job data:', error);
        showAlert('Error loading job data', 'error');
    }
}

// Convert datetime format
function convertToDatetimeLocal(dateStr) {
    // Convert "DD/MM - HH:MM" to "YYYY-MM-DDTHH:MM"
    if (!dateStr) return '';
    
    try {
        const [datePart, timePart] = dateStr.split(' - ');
        const [day, month] = datePart.split('/');
        const currentYear = new Date().getFullYear();
        
        return `${currentYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T${timePart}`;
    } catch (error) {
        return '';
    }
}

function convertFromDatetimeLocal(datetimeLocal) {
    // Convert "YYYY-MM-DDTHH:MM" to "DD/MM - HH:MM"
    if (!datetimeLocal) return '';
    
    try {
        const date = new Date(datetimeLocal);
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        
        return `${day}/${month} - ${hours}:${minutes}`;
    } catch (error) {
        return '';
    }
}

// Form submission
document.getElementById('job-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const jobData = {
        mesin: formData.get('mesin') || document.getElementById('mesin').value,
        job_type: formData.get('job_type'),
        MODEL: formData.get('MODEL') || document.getElementById('MODEL').value,
        PART: formData.get('PART') || document.getElementById('PART').value,
        SIZE: formData.get('SIZE') || document.getElementById('SIZE').value,
        START: convertFromDatetimeLocal(document.getElementById('START').value),
        FINISH: convertFromDatetimeLocal(document.getElementById('FINISH').value),
        ETC_H: formData.get('ETC_H') || document.getElementById('ETC_H').value,
        OPERATOR: formData.get('OPERATOR') || document.getElementById('OPERATOR').value,
        REMARK: formData.get('REMARK') || document.getElementById('REMARK').value
    };
    
    try {
        const url = currentEditingJobId ? `/edit_job/${currentEditingJobId}` : '/add_job';
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            closeModal();
            loadDashboardData();
        } else {
            showAlert(result.message, 'error');
        }
        
    } catch (error) {
        console.error('Error saving job:', error);
        showAlert('Error saving job', 'error');
    }
});

// Finish job
async function finishJob(jobId) {
    if (!confirm('Apakah Anda yakin ingin menyelesaikan job ini?')) {
        return;
    }
    
    try {
        const response = await fetch(`/finish_job/${jobId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadDashboardData();
        } else {
            showAlert(result.message, 'error');
        }
        
    } catch (error) {
        console.error('Error finishing job:', error);
        showAlert('Error finishing job', 'error');
    }
}

// Navigate job
async function navigateJob(machine, direction) {
    try {
        // Get current next job index and current job id
        const currentIndex = nextJobIndices[machine] || 0;
        const currentJob = dashboardData[machine]?.next_jobs?.[currentIndex];
        const currentJobId = currentJob ? currentJob.id : null;

        // Fetch new job from backend with current_job_id param
        const url = new URL(`/navigate_job/${machine}/${direction}`, window.location.origin);
        if (currentJobId) {
            url.searchParams.append('current_job_id', currentJobId);
        }

        const response = await fetch(url);
        const result = await response.json();

        if (result.job) {
            // Find index of new job in next_jobs array
            const nextJobs = dashboardData[machine]?.next_jobs || [];
            const newIndex = nextJobs.findIndex(job => job.id === result.job.id);

            if (newIndex !== -1) {
                nextJobIndices[machine] = newIndex;
            } else {
                // If not found, reset to 0
                nextJobIndices[machine] = 0;
            }

            // Update dashboardData for this machine's next job
            dashboardData[machine].next_jobs[nextJobIndices[machine]] = result.job;

            // Re-render dashboard
            renderDashboard();
        }

    } catch (error) {
        console.error('Error navigating job:', error);
        showAlert('Error navigating job', 'error');
    }
}

// Alert function
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `fixed top-4 right-4 z-50 p-4 rounded-lg font-semibold slide-in ${
        type === 'success' ? 'bg-green-600' : 
        type === 'error' ? 'bg-red-600' : 
        'bg-blue-600'
    }`;
    alertDiv.textContent = message;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Close modal when clicking outside
document.getElementById('job-modal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('job-modal')) {
        closeModal();
    }
});

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    // Refresh data every 30 seconds
    setInterval(loadDashboardData, 30000);
});
