console.log('payments/stripe.js');

fetch("/billing/stripe/config/")
  .then((result) => {
    return result.json();
  })
  .then((data) => {
    const stripe = Stripe(data.publicKey);

    let amount = $('#amount').val();
    let currency = $('#currency').val();
    let receipt = $('#receipt').val();
    // console.log(amount);
    // console.log(currency);
    // console.log(receipt);

    document.querySelector("#submitBtn").addEventListener("click", () => {
      // Get Checkout Session ID
      fetch("/billing/stripe/create-checkout-session/?amount="+amount+"&currency="+currency+"&receipt="+receipt)
        .then((result) => {
          return result.json();
        })
        .then((data) => {
          console.log(data);
          // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({sessionId: data.sessionId})
        })
        .then((res) => {
          console.log(res);
        });
    });
  });
