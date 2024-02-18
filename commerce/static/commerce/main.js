const customSuccessColor = getComputedStyle(document.documentElement).getPropertyValue('--custom-success');
const customDarkColor = getComputedStyle(document.documentElement).getPropertyValue('--custom-dark');
const customInfoColor = getComputedStyle(document.documentElement).getPropertyValue('--custom-primary');
const customDangerColor = getComputedStyle(document.documentElement).getPropertyValue('--custom-danger');


document.addEventListener('DOMContentLoaded', function () {

    (function () {
        attachLoaderOnClick();
        handleCategoryLinks();
    })();

    if (document.querySelector('#listings-section')) {
        handleFiltering();

        // Show/hide the scroll-to-top button based on scroll position
        $(window).scroll(function () {
            if ($(this).scrollTop() > 100) {
                $('#scroll-to-to-btn').fadeIn();
            } else {
                $('#scroll-to-to-btn').fadeOut();
            }
        });

        // Scroll to top when the button is clicked
        $('#scroll-to-to-btn').click(function () {
            $('html, body').animate({ scrollTop: 0 }, 200);
            return false;
        });

    }

    // Check if the payment elements exist on the page before invoking the function
    if (document.querySelector('#payment-form')) {
        handlePaymentOptions();
    }

    if (document.querySelector('.listing-images')) {
        showEnlargedImageModal();
    }
});


function attachLoaderOnClick() {
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('loader-on-click')) {
            var button = event.target;
            button.disabled = true;

            var form = button.closest('form');
            if (form) {
                var hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'loading_indicator';
                hiddenInput.value = 'true';
                form.appendChild(hiddenInput);

                // Attach a listener to the form's submit event
                form.addEventListener('submit', function () {
                    // Reset the button's state and content upon form submission
                    button.disabled = false;
                    button.innerHTML = 'Submit'; // Replace with the original content
                });
            }

            button.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Loading...
            `;

            if (form) {
                form.submit();
            }
        }
    });

    // Attach a listener to the window's unload event
    window.addEventListener('unload', function () {
        // Reset the button's state and content when the user navigates away from the page
        var buttons = document.querySelectorAll('.loader-on-click');
        buttons.forEach(function (button) {
            button.disabled = false;
            button.innerHTML = 'Submit'; // Replace with the original content
        });
    });
}

function handleCategoryLinks() {
    var categoryLinks = document.querySelectorAll('.category-link');
    var previousActiveLink = null;
    categoryLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();

            // Remove 'active' class from all category links
            categoryLinks.forEach(function (otherLink) {
                if (otherLink.classList.contains('active')) {
                    previousActiveLink = otherLink;
                    otherLink.classList.remove('active');
                }
            });

            // Add 'active' class to the clicked category link
            this.classList.add('active');

            var categoryValue = this.getAttribute('data-category');

            // Uncheck all other category checkboxes
            var checkboxes = document.querySelectorAll('.category-checkbox');
            var targetCheckbox = null;

            checkboxes.forEach(function (checkbox) {

                if (checkbox.value !== categoryValue) {
                    checkbox.checked = false;
                    if (checkbox.value === previousActiveLink.getAttribute('data-category') && categoryValue === 'all') {
                        // Trigger the change event to execute the filtering script

                        console.log('Triggering change event for checkbox:', checkbox);
                        var event = new Event('change');
                        checkbox.dispatchEvent(event);

                    }
                } else {
                    targetCheckbox = checkbox;
                }
            });

            if (targetCheckbox) {
                targetCheckbox.checked = true;
                // Trigger the change event to execute the filtering script
                var event = new Event('change');
                targetCheckbox.dispatchEvent(event);
            }

            // Scroll to the listings-section
            var listingsSection = document.getElementById('listings-section');
            if (listingsSection) {
                listingsSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}


function handleFiltering() {
    var baseUrl = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ":" + window.location.port : "") + "/filter/";
    var currentPage = 1
    var delay = 500;
    var rangeTimeout;
    const mobileScreenWidth = 768;
    var sortOption = 'best-match'


    function attachSortOptionListener() {
        $('.sort-option').click(function () {
            sortOption = $(this).data('sort');
            updateListings();
        });
    }

    // Handle checkbox change event
    $('.filter-checkbox').change(updateListings);

    $('#mobile_price_range').on('input', function () {
        // Clear the previous timeout
        clearTimeout(rangeTimeout);
        // Set a new timeout to call the updateListings function after the specified delay
        rangeTimeout = setTimeout(updateListings, delay);
    });


    // Handle range input change event
    $('#desktop_price_range').on('input', function () {
        // Clear the previous timeout
        clearTimeout(rangeTimeout);
        // Set a new timeout to call the updateListings function after the specified delay
        rangeTimeout = setTimeout(updateListings, delay);
    });

    $(document).on('click', '.page-link', function () {
        var val = $(this).data('label');
        if (val == "previous") {
            if (currentPage > 1) {
                currentPage = currentPage - 1;
            }
        }
        else if (val == "next") {
            currentPage = currentPage + 1;
        }

        else {
            currentPage = val;
        }
        updateListings();

    });

    // Handle remove filter click event
    $(document).on('click', '.remove-filter', function () {
        var labelToRemove = $(this).data('label');
        $('.filter-checkbox[data-filter-type="' + labelToRemove + '"]').prop('checked', false);

        // Trigger the updateListings function
        updateListings();
    });

    attachSortOptionListener();

    function updateListings() {
        var selectedFilters = {
            'page': currentPage,
            'sort': sortOption
        };

        // Collect selected filters
        $('.filter-checkbox:checked').each(function () {
            var filterType = $(this).data('filter-type');
            var filterValue = $(this).val();
            if (!selectedFilters.hasOwnProperty(filterType)) {
                selectedFilters[filterType] = [];
            }

            // Add the filter value to the array
            selectedFilters[filterType].push(filterValue);
        });

        if (window.innerWidth < mobileScreenWidth) {
            var rangeValue = $('#mobile_price_range').val();
        }
        else {
            var rangeValue = $('#desktop_price_range').val();
        }
        selectedFilters['price_range'] = [rangeValue];

        // Construct the URL with query parameters
        var dynamicUrl = baseUrl + "?" + $.param(selectedFilters);
        // Send AJAX request to update listings
        $.ajax({
            type: 'GET',
            url: dynamicUrl,
            success: function (data) {
                $('#listings-container').html(data);
                attachSortOptionListener();
            },
            error: function () {
                console.error('Error occurred while updating listings.');
            }
        });
    }

}

function confirmCounterOffer(link) {
    Swal.fire({
        title: 'Accept Counter Offer?',
        icon: 'success',
        showCancelButton: true,
        confirmButtonColor: customSuccessColor,
        cancelButtonColor: customDarkColor,
        confirmButtonText: 'Yes, accept offer!',
        cancelButtonText: 'Go Back'
    }).then((result) => {
        if (result.isConfirmed) {
            // Get all elements with the class name 'counter-offer-btn'
            document.getElementById('counter-offer-table').innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Loading...
                `;

            // Redirect to the href link
            window.location.href = link;
        }
    });
}
function rejectCounterOffer(link) {
    Swal.fire({
        title: 'Reject Counter Offer?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: customDangerColor,
        cancelButtonColor: customDarkColor,
        confirmButtonText: 'Yes, Reject offer.',
        cancelButtonText: 'Go Back'
    }).then((result) => {
        if (result.isConfirmed) {
            // Get all elements with the class name 'counter-offer-btn'
            document.getElementById('counter-offer-table').innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Loading...
                `;

            // Redirect to the href link
            window.location.href = link;
        }
    });
}


function confirmOffer(link) {
    Swal.fire({
        title: 'Accept Offer?',
        text: 'By accepting this offer, all other offers and counter offers will be automatically rejected, and the purchase will be confirmed irreversibly.',
        icon: 'success',
        showCancelButton: true,
        confirmButtonColor: customSuccessColor,
        cancelButtonColor: customDarkColor,
        confirmButtonText: 'Yes, accept offer!',
        cancelButtonText: 'Go Back'
    }).then((result) => {
        if (result.isConfirmed) {
            // Show loading spinner
            document.getElementById('ongoing-offers-table').innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Loading...
                `;

            // Redirect to the href link
            window.location.href = link;
        }
    });
}

function rejectOffer(link) {
    Swal.fire({
        title: 'Reject Offer?',
        text: 'Are you sure you want to reject this offer? This cannot be undone.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: customDangerColor,
        cancelButtonColor: customDarkColor,
        confirmButtonText: 'Yes, reject offer.',
        cancelButtonText: 'Go Back'
    }).then((result) => {
        if (result.isConfirmed) {
            // Show loading spinner
            document.getElementById('ongoing-offers-table').innerHTML = `
                        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                        Loading...
                    `;
            // Redirect to the href link
            window.location.href = link;
        }
    });
}

function confirmListingClose(link) {
    Swal.fire({
        title: 'Close Offer?',
        text: 'Are you sure you want to close your listing. If your listing had no bids/offers your listing will remain unsold, This process cannot be undone.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: customDangerColor,
        cancelButtonColor: customDarkColor,
        confirmButtonText: 'Yes, Close Listing!',
        cancelButtonText: 'Go Back'
    }).then((result) => {
        if (result.isConfirmed) {
            // Show loading spinner
            document.getElementById('active-listings-table').innerHTML = `
                        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                        Loading...
                    `;
            // Redirect to the href link
            window.location.href = link;
        }
    });
}

function confirmCounterOfferFormSubmit(index) {
    Swal.fire({
        title: 'Send Counter Offer?',
        text: 'Sending a counter offer will nullify this offer if rejected by the buyer.',
        icon: 'info',
        showCancelButton: true,
        confirmButtonColor: customSuccessColor,
        cancelButtonColor: customDarkColor,
        confirmButtonText: 'Send Counter Offer',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            // Submit the form
            document.getElementById(`counter-offer-form-${index}`).submit();
            // Show loading spinner
            document.getElementById('counter-offer-form-${index}').innerHTML = `
                        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                        Loading...
                    `;
        }
    });
}

function confirmProfileChange() {
    Swal.fire({
        title: 'Are you sure?',
        text: 'Email/Password change process will deactivate your account till you have verified it.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: customSuccessColor,
        cancelButtonColor: customDarkColor,
        confirmButtonText: 'Yes, change it!'
    }).then((result) => {
        if (result.isConfirmed) {
            // Perform the action if the user confirms
            document.getElementById('email-form-button').innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Loading...
            `;
            document.getElementById('email-form').submit();
        }
    });
}

function handlePaymentOptions() {
    var paymentOptionSelect = document.querySelector('#id_payment_option');
    var cardPaymentDiv = document.querySelector('#card-payment');
    var bkashPaymentDiv = document.querySelector('#bkash-payment');

    // Initial toggle based on selected payment option
    togglePaymentForms();

    // Event listener for changes in the payment option
    paymentOptionSelect.addEventListener('change', togglePaymentForms);

    function togglePaymentForms() {
        var selectedOption = paymentOptionSelect.value;

        // Toggle visibility based on selected payment option
        cardPaymentDiv.style.display = (selectedOption === 'CC' || selectedOption === 'DC') ? 'block' : 'none';
        bkashPaymentDiv.style.display = (selectedOption === 'B') ? 'block' : 'none';

        // Add or remove the 'required' attribute based on visibility
        Array.from(cardPaymentDiv.querySelectorAll('input')).forEach(function (input) {
            input.required = (selectedOption === 'CC' || selectedOption === 'DC');
        });

        Array.from(bkashPaymentDiv.querySelectorAll('input')).forEach(function (input) {
            input.required = (selectedOption === 'B');
        });
    }
}


function showEnlargedImageModal() {
    // Get all images
    var images = document.querySelectorAll('.listing-images');

    // Add click event listener to each image
    images.forEach(function (image) {
        image.addEventListener('click', function () {
            // Get the source of the clicked image
            var src = this.getAttribute('src');

            // Set the source of the modal image
            var modalImage = document.getElementById('modalImage');
            modalImage.setAttribute('src', src);

            // Show the modal
            var modal = new bootstrap.Modal(document.getElementById('imageModal'));
            modal.show();
        });
    });
}


