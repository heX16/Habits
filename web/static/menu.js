/**
 * Creates and manages a floating menu.
 */
class FloatingMenu {
    constructor(options = {}) {
        this.currentMenu = null;
        this.options = {
            className: options.className || 'floating-menu',
            itemClassName: options.itemClassName || 'menu-item',
            position: options.position || 'below', // 'below' or 'auto'
            style: options.style || {
                backgroundColor: 'white',
                border: '1px solid #ccc',
                padding: '5px',
                boxShadow: '2px 2px 6px rgba(0,0,0,0.2)',
                zIndex: 1000
            }
        };

        // Bind event listener for closing menu
        this.handleDocumentClick = this.handleDocumentClick.bind(this);
        document.addEventListener('click', this.handleDocumentClick);
    }

    /**
     * Shows the menu near the specified element
     * @param {HTMLElement} targetElement - Element to show menu near
     * @param {Array} items - Array of menu items
     * @param {Object} options - Optional override of default options
     */
    show(targetElement, items, options = {}) {
        this.remove();

        const menu = document.createElement('div');
        menu.className = this.options.className;
        Object.assign(menu.style, this.options.style, options.style || {});

        // Create menu items
        items.forEach(item => {
            const row = document.createElement('div');
            row.className = this.options.itemClassName;
            row.style.cursor = 'pointer';
            
            if (typeof item.render === 'function') {
                // Custom render function
                item.render(row);
            } else {
                // Default rendering
                if (item.icon) {
                    const iconCell = document.createElement('span');
                    iconCell.textContent = item.icon;
                    iconCell.style.marginRight = '8px';
                    row.appendChild(iconCell);
                }

                const labelCell = document.createElement('span');
                labelCell.textContent = item.label;
                row.appendChild(labelCell);
            }

            if (item.onClick) {
                row.addEventListener('click', (e) => {
                    e.stopPropagation();
                    item.onClick(e);
                    this.remove();
                });
            }

            menu.appendChild(row);
        });

        // Position the menu
        const rect = targetElement.getBoundingClientRect();
        if (this.options.position === 'below' || this.options.position === 'auto') {
            menu.style.position = 'absolute';
            menu.style.top = (rect.bottom + window.scrollY) + 'px';
            menu.style.left = (rect.left + window.scrollX) + 'px';
        }

        document.body.appendChild(menu);
        this.currentMenu = menu;
    }

    /**
     * Removes the current menu if it exists
     */
    remove() {
        if (this.currentMenu) {
            this.currentMenu.remove();
            this.currentMenu = null;
        }
    }

    /**
     * Handles clicks outside the menu to close it
     */
    handleDocumentClick(e) {
        if (this.currentMenu && !this.currentMenu.contains(e.target)) {
            this.remove();
        }
    }

    /**
     * Cleanup when the menu is no longer needed
     */
    destroy() {
        document.removeEventListener('click', this.handleDocumentClick);
        this.remove();
    }
}

// URL: http://server.test/habits/static/menu.js
// Used on: http://server.test/habits/ 