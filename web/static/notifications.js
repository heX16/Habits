class NotificationManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        if (container) {
            return container;
        }
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'error') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        const messageText = document.createElement('span');
        messageText.textContent = message;
        notification.appendChild(messageText);

        const closeButton = document.createElement('button');
        closeButton.className = 'notification-close';
        closeButton.textContent = '×';
        closeButton.onclick = () => this.hide(notification);
        notification.appendChild(closeButton);

        this.container.appendChild(notification);

        // Hide automatically after 5 seconds
        setTimeout(() => this.hide(notification), 5000);

        return notification;
    }

    hide(notification) {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            if (notification.parentNode === this.container) {
                this.container.removeChild(notification);
            }
        }, 300); // Animation duration
    }
}