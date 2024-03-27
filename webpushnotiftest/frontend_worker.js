self.addEventListener('push', function(event) {
    console.log("Push received: ", event.data.json());
    if (event.data) {
        const data = event.data.json();
        self.registration.showNotification(
            data.title,
            {body: data.body}
        );
    } else {
        show_error("Push notification fail: ", "error in frontend_worker");
    }
});
