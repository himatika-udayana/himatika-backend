(function () {
    function toggleField(selector, show) {
        const row = document.querySelector(selector);

        if (!row) return;

        row.style.display = show ? "" : "none";
    }

    function updateFields() {
        const tipe = document.getElementById("id_tipe");

        if (!tipe) return;

        const value = tipe.value;

        // Event
        toggleField(".field-tanggal_event", value === "event");
        toggleField(".field-lokasi_event", value === "event");

        // Open Requirement
        toggleField(".field-link_formulir", value === "open-requirement");
        toggleField(".field-deadline_formulir", value === "open-requirement");

        // Prestasi
        toggleField(".field-level_prestasi", value === "prestasi");

        // Mathpedia
        toggleField(".field-kategori_mathpedia", value === "mathpedia");
        toggleField(".field-tags", value === "mathpedia");
    }

    document.addEventListener("DOMContentLoaded", function () {
        updateFields();

        const tipe = document.getElementById("id_tipe");

        if (tipe) {
            tipe.addEventListener("change", updateFields);
        }
    });
})();