// Journal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-save functionality for journal entries
    const contentTextarea = document.getElementById('content');
    const titleInput = document.getElementById('title');
    let autoSaveTimer;
    
    // Auto-resize textarea
    function autoResize(textarea) {
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 500) + 'px';
        }
    }
    
    // Initialize auto-resize for content textarea
    if (contentTextarea) {
        contentTextarea.addEventListener('input', function() {
            autoResize(this);
            
            // Clear existing timer
            clearTimeout(autoSaveTimer);
            
            // Set new timer for auto-save draft
            autoSaveTimer = setTimeout(() => {
                saveDraft();
            }, 2000); // Save draft after 2 seconds of inactivity
        });
        
        // Initial resize
        autoResize(contentTextarea);
    }
    
    // Auto-save draft functionality
    function saveDraft() {
        if (!titleInput || !contentTextarea) return;
        
        const title = titleInput.value.trim();
        const content = contentTextarea.value.trim();
        
        if (title || content) {
            const draft = {
                title: title,
                content: content,
                timestamp: new Date().toISOString()
            };
            
            try {
                localStorage.setItem('journal_draft', JSON.stringify(draft));
                showDraftStatus('Draft saved automatically', 'success');
            } catch (error) {
                console.error('Failed to save draft:', error);
                showDraftStatus('Failed to save draft', 'error');
            }
        }
    }
    
    // Load draft on page load
    function loadDraft() {
        try {
            const draft = localStorage.getItem('journal_draft');
            if (draft && titleInput && contentTextarea) {
                const draftData = JSON.parse(draft);
                
                // Only load if fields are currently empty
                if (!titleInput.value && !contentTextarea.value) {
                    titleInput.value = draftData.title || '';
                    contentTextarea.value = draftData.content || '';
                    autoResize(contentTextarea);
                    
                    if (draftData.title || draftData.content) {
                        showDraftStatus('Draft restored', 'info');
                    }
                }
            }
        } catch (error) {
            console.error('Failed to load draft:', error);
        }
    }
    
    // Clear draft when form is successfully submitted
    function clearDraft() {
        try {
            localStorage.removeItem('journal_draft');
        } catch (error) {
            console.error('Failed to clear draft:', error);
        }
    }
    
    // Show draft status message
    function showDraftStatus(message, type) {
        // Remove existing status
        const existingStatus = document.getElementById('draft-status');
        if (existingStatus) {
            existingStatus.remove();
        }
        
        // Create new status
        const status = document.createElement('div');
        status.id = 'draft-status';
        status.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
        status.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 200px;';
        status.innerHTML = `
            <small>${message}</small>
            <button type="button" class="btn-close btn-close-sm" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(status);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (status.parentElement) {
                status.remove();
            }
        }, 3000);
    }
    
    // Load draft on page load
    loadDraft();
    
    // Handle form submission
    const journalForm = document.querySelector('form[method="POST"]');
    if (journalForm) {
        journalForm.addEventListener('submit', function(e) {
            const title = titleInput?.value.trim();
            const content = contentTextarea?.value.trim();
            
            if (!title || !content) {
                e.preventDefault();
                showDraftStatus('Please provide both a title and content', 'error');
                return;
            }
            
            // Clear draft on successful submission
            clearDraft();
            
            // Show loading state
            const submitButton = journalForm.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalHTML = submitButton.innerHTML;
                submitButton.innerHTML = '<i data-feather="loader" class="me-2"></i>Saving...';
                submitButton.disabled = true;
                
                // Re-enable button after form submission (in case of errors)
                setTimeout(() => {
                    submitButton.innerHTML = originalHTML;
                    submitButton.disabled = false;
                    feather.replace();
                }, 3000);
            }
        });
    }
    
    // Word count functionality
    if (contentTextarea) {
        const wordCountDisplay = document.createElement('div');
        wordCountDisplay.className = 'text-muted small mt-2';
        wordCountDisplay.id = 'word-count';
        contentTextarea.parentElement.appendChild(wordCountDisplay);
        
        function updateWordCount() {
            const text = contentTextarea.value.trim();
            const words = text ? text.split(/\s+/).length : 0;
            const characters = text.length;
            
            wordCountDisplay.textContent = `${words} words, ${characters} characters`;
        }
        
        contentTextarea.addEventListener('input', updateWordCount);
        updateWordCount(); // Initial count
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+S or Cmd+S to save draft
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveDraft();
            showDraftStatus('Draft saved manually', 'success');
        }
        
        // Ctrl+Enter or Cmd+Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && journalForm) {
            e.preventDefault();
            journalForm.requestSubmit();
        }
    });
    
    // Journal card interactions on journal list page
    const journalCards = document.querySelectorAll('.journal-card');
    journalCards.forEach(card => {
        // Add hover effect with emotion color
        card.addEventListener('mouseenter', function() {
            const emotionBadge = this.querySelector('[class*="emotion-"]');
            if (emotionBadge) {
                const emotionClass = Array.from(emotionBadge.classList).find(cls => cls.startsWith('emotion-'));
                if (emotionClass) {
                    this.style.borderLeftColor = getComputedStyle(emotionBadge).color;
                    this.style.borderLeftWidth = '4px';
                }
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.borderLeftColor = '';
            this.style.borderLeftWidth = '';
        });
        
        // Add click handler for better mobile experience
        card.addEventListener('click', function(e) {
            if (e.target.closest('a')) return; // Don't interfere with existing links
            
            const readMoreLink = this.querySelector('a[href*="view_journal_entry"]');
            if (readMoreLink) {
                readMoreLink.click();
            }
        });
    });
    
    // Emotion analysis display for journal view page
    const emotionBadge = document.querySelector('.emotion-badge');
    if (emotionBadge) {
        // Add tooltip with emotion explanation
        emotionBadge.title = getEmotionDescription(emotionBadge.textContent.toLowerCase());
        emotionBadge.style.cursor = 'help';
    }
    
    // Helper function to get emotion descriptions
    function getEmotionDescription(emotion) {
        const descriptions = {
            'joy': 'Feeling happy, pleased, or delighted',
            'sadness': 'Feeling down, melancholic, or sorrowful',
            'anger': 'Feeling irritated, frustrated, or furious',
            'fear': 'Feeling scared, anxious, or worried',
            'surprise': 'Feeling amazed, astonished, or unexpected',
            'love': 'Feeling affectionate, caring, or romantic',
            'neutral': 'Balanced emotional state'
        };
        
        return descriptions[emotion.replace(/[()%0-9\s]/g, '').toLowerCase()] || 'Detected emotional state';
    }
    
    // Search functionality for journal entries (if search input exists)
    const searchInput = document.getElementById('journal-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterJournalEntries(this.value.toLowerCase());
            }, 300);
        });
        
        function filterJournalEntries(searchTerm) {
            const journalCards = document.querySelectorAll('.journal-card');
            let visibleCount = 0;
            
            journalCards.forEach(card => {
                const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
                const content = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
                const isVisible = title.includes(searchTerm) || content.includes(searchTerm);
                
                card.parentElement.style.display = isVisible ? 'block' : 'none';
                if (isVisible) visibleCount++;
            });
            
            // Show/hide "no results" message
            updateSearchResults(visibleCount, searchTerm);
        }
        
        function updateSearchResults(count, searchTerm) {
            let noResultsMsg = document.getElementById('no-search-results');
            
            if (count === 0 && searchTerm) {
                if (!noResultsMsg) {
                    noResultsMsg = document.createElement('div');
                    noResultsMsg.id = 'no-search-results';
                    noResultsMsg.className = 'col-12 text-center py-5';
                    noResultsMsg.innerHTML = `
                        <i data-feather="search" style="width: 48px; height: 48px;" class="text-muted mb-3"></i>
                        <h5 class="text-muted">No entries found</h5>
                        <p class="text-muted">Try adjusting your search terms</p>
                    `;
                    
                    const journalGrid = document.querySelector('.row.g-4');
                    if (journalGrid) {
                        journalGrid.appendChild(noResultsMsg);
                        feather.replace();
                    }
                }
            } else if (noResultsMsg) {
                noResultsMsg.remove();
            }
        }
    }
    
    // Initialize tooltips for emotion badges
    const emotionBadges = document.querySelectorAll('.emotion-badge');
    emotionBadges.forEach(badge => {
        if (!badge.title) {
            badge.title = getEmotionDescription(badge.textContent);
        }
    });
});
