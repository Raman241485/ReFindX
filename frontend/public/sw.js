// ============================================================
// REFindX SERVICE WORKER
// PUSH NOTIFICATIONS
// ============================================================

self.addEventListener("push", (event) => {

  let data = {
    title: "ReFindX",
    body: "You have a new notification.",
    icon: "/refindx-logo.png",
  };


  // ==========================================================
  // READ PUSH DATA
  // ==========================================================

  try {

    if (event.data) {
      data = event.data.json();
    }

  } catch (error) {

    console.error(
      "Push data error:",
      error
    );

  }


  // ==========================================================
  // SHOW NOTIFICATION
  // ==========================================================

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

        // Allow normal notification sound
        silent: false,

        // Keep normal OS notification behavior
        requireInteraction: false,

        // Store data for notification click
        data: {
          item_id:
            data.item_id || null,

          notification_id:
            data.notification_id || null,

          url:
            data.url || "/notifications",
        },

      }

    )

  );

});


// ============================================================
// NOTIFICATION CLICK
// ============================================================

self.addEventListener(
  "notificationclick",
  (event) => {

    event.notification.close();


    // --------------------------------------------------------
    // GET NOTIFICATION DATA
    // --------------------------------------------------------

    const notificationData =
      event.notification.data || {};


    const itemId =
      notificationData.item_id;


    const notificationUrl =
      notificationData.url ||
      "/notifications";


    // --------------------------------------------------------
    // DECIDE WHERE TO OPEN
    // --------------------------------------------------------

    let url =
      notificationUrl;


    if (itemId) {

      url =
        `/items/${itemId}`;

    }


    // --------------------------------------------------------
    // OPEN / FOCUS REFINDX
    // --------------------------------------------------------

    event.waitUntil(

      clients
        .matchAll({
          type: "window",
          includeUncontrolled: true,
        })

        .then((clientList) => {

          // --------------------------------------------------
          // EXISTING REFINDX TAB
          // --------------------------------------------------

          for (const client of clientList) {

            if (
              client.url.includes(
                "refindx-frontend.onrender.com"
              )
            ) {

              if ("focus" in client) {

                client.focus();

              }

              if ("navigate" in client) {

                return client.navigate(
                  url
                );

              }

              return;

            }

          }


          // --------------------------------------------------
          // OPEN NEW REFINDX TAB
          // --------------------------------------------------

          if (clients.openWindow) {

            return clients.openWindow(
              url
            );

          }

        })

    );

  }
);