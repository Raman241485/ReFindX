self.addEventListener("push", (event) => {
  let data = {
    title: "ReFindX",
    body: "You have a new notification.",
    icon: "/refindx-logo.png",
  };

  try {
    if (event.data) {
      data = event.data.json();
    }
  } catch (error) {
    console.error("Push data error:", error);
  }

  event.waitUntil(
    self.registration.showNotification(
      data.title || "ReFindX",
      {
        body:
          data.body ||
          "You have a new notification.",
        icon:
          data.icon ||
          "/refindx-logo.png",
        badge:
          data.icon ||
          "/refindx-logo.png",
        data: data,
      }
    )
  );
});


self.addEventListener(
  "notificationclick",
  (event) => {

    event.notification.close();

    const itemId =
      event.notification.data?.item_id;

    let url = "/notifications";

    if (itemId) {
      url = `/items/${itemId}`;
    }

    event.waitUntil(
      clients.matchAll({
        type: "window",
        includeUncontrolled: true,
      }).then((clientList) => {

        for (const client of clientList) {

          if ("focus" in client) {

            client.focus();

            if ("navigate" in client) {
              client.navigate(url);
            }

            return;
          }
        }

        if (clients.openWindow) {
          return clients.openWindow(url);
        }

      })
    );
  }
);