<script>
    // Function to auto-generate signature
    function generateSignature() {
        var currentTime = new Date();
        var formattedTime = currentTime.toISOString().slice(2, 10).replace(/-/g, '') + '-' + currentTime.getHours() +
            currentTime.getMinutes() + currentTime.getSeconds();
        document.getElementById("transaction_uuid").value = formattedTime;
        var total_amount = document.getElementById("total_amount").value;
        var transaction_uuid = document.getElementById("transaction_uuid").value;
        var product_code = document.getElementById("product_code").value;
        var secret = document.getElementById("secret").value;

        var hash = CryptoJS.HmacSHA256(
            `total_amount=${total_amount},transaction_uuid=${transaction_uuid},product_code=${product_code}`,
            `${secret}`);
        var hashInBase64 = CryptoJS.enc.Base64.stringify(hash);
        document.getElementById("signature").value = hashInBase64;
    }

    // Event listeners to call generateSignature() when inputs are changed
    document.getElementById("total_amount").addEventListener("input", generateSignature);
    document.getElementById("transaction_uuid").addEventListener("input", generateSignature);
    document.getElementById("product_code").addEventListener("input", generateSignature);
    document.getElementById("secret").addEventListener("input", generateSignature);
</script>