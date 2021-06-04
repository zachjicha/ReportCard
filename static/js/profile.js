// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        reviews: [],
        is_editing: false,
        edit_text: "",
        edit_stars_displayed: 0,
        edit_rating: 0,
        author_email: author_email,
        logged_in: logged_in,
        user_id: user_id,
        //has_pfp: has_pfp,
        //uploading: false,
        //deleting: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };
    /*
    app.upload_pfp = function (event) {

        let input = event.target;
        let file = input.files[0];
        if (file) {

            // from https://roufid.com/javascript-check-file-image/
            const acceptedImageTypes = ['image/jpeg', 'image/png'];

            // If file is not image, fail
            if(!acceptedImageTypes.includes(file.type)) {
                alert("Only jpeg and png files are accepted");
                return;
            }

            app.vue.uploading = true;
            let file_type = file.type;
            let file_name = file.name;
            // Requests the upload URL.
            axios.post(access_pfp_url, {
                action: "PUT",
                file_name: file_name,
                file_type: file_type,
            }).then ((r) => {
                let upload_url = r.data.signed_url;
                console.log(upload_url);
                let file_path = r.data.file_path;
                // Uploads the file, using the low-level interface.
                let req = new XMLHttpRequest();
                // We listen to the load event = the file is uploaded, and we call upload_complete.
                // That function will notify the server `of the location of the image.
                req.addEventListener("load", function () {
                    app.upload_complete(file_name, file_path);
                });

                // Clean up on error
                req.addEventListener("error", function () {
                    alert("Image upload failed!");
                    app.vue.uploading = false;
                    return;
                });

                req.open("PUT", upload_url, true);
                req.send(file);
            });
        }
    }

    app.upload_complete = function (file_name, file_path) {
        // We need to let the server know that the upload was complete;
        axios.post(notify_upload_pfp_url, {
            file_name: file_name,
            file_path: file_path,
        }).then( function (r) {
            app.vue.uploading = false;
            // Reload so changes take effect
            //window.location.reload();
        });
    }

    app.delete_pfp = function () {
        if (!app.vue.delete_confirmation) {
            // Ask for confirmation before deleting it.
            app.vue.delete_confirmation = true;
        } else {
            // It's confirmed.
            app.vue.delete_confirmation = false;
            app.vue.deleting = true;
            // Obtains the delete URL.
            let file_path = app.vue.file_path;
            axios.post(access_pfp_url, {
                action: "DELETE",
                file_path: file_path,
            }).then(function (r) {
                let delete_url = r.data.signed_url;
                if (delete_url) {
                    // Performs the deletion request.
                    let req = new XMLHttpRequest();
                    req.addEventListener("load", function () {
                        app.deletion_complete(file_path);
                    });

                    // Clean up on error
                    req.addEventListener("error", function () {
                        alert("Image delete failed!");
                        app.vue.deleting = false;
                        return;
                    });

                    req.open("DELETE", delete_url);
                    req.send();
                }
            });
        }
    }

    app.deletion_complete = function (file_path) {
        // We need to notify the server that the file has been deleted on GCS.
        axios.post(notify_delete_pfp_url, {
            file_path: file_path,
        }).then (function (r) {
            // Poof, no more file.
            app.vue.deleting =  false;
            // Reload so changes take effect
            window.location.reload();
        })
    }*/

    app.edit_stars_out = function () {
        app.vue.edit_stars_displayed = app.vue.edit_rating;
    }

    app.edit_set_star = function (star_idx) {
        app.vue.edit_rating = star_idx;
    }

    app.edit_star_over = function (star_idx) {
        app.vue.edit_stars_displayed = star_idx;
    }

    app.start_edit = function (rev_idx) {
        if(!app.vue.is_editing) {
            app.vue.reviews[rev_idx].is_editing = true;
            app.vue.is_editing = true;
            app.vue.edit_text = app.vue.reviews[rev_idx].body;
            app.vue.edit_stars_displayed = app.vue.reviews[rev_idx].rating;
            app.vue.edit_rating = app.vue.edit_stars_displayed;
        }
    }

    app.save_edit = function (rev_idx, rev_id) {
        axios.post(
            edit_review_url,
            {
                id: rev_id,
                body: app.vue.edit_text,
                rating: app.vue.edit_rating,
            }
        ).then(function (response) {
            app.vue.reviews[rev_idx].is_editing = false;
            app.vue.reviews[rev_idx].body = app.vue.edit_text;
            app.vue.reviews[rev_idx].rating = app.vue.edit_rating;
            app.vue.is_editing = false;
            app.vue.edit_text = "";
            app.calculate_rating();
        });
    }

    app.cancel_edit = function (rev_idx) {
        app.vue.reviews[rev_idx].is_editing = false;
        app.vue.is_editing = false;
        app.vue.edit_text = "";
        app.vue.edit_stars_displayed = 0;
    }

    app.delete_review = function (rev_idx) {
        let id = app.vue.reviews[rev_idx].id;
        axios.post(
            delete_review_url,
            {id: id}
        ).then(function () {
           for(let i = 0; i < app.vue.reviews.length; i++) {
               if(app.vue.reviews[i].id === id) {
                   app.vue.reviews.splice(i, 1);
                   app.enumerate(app.vue.reviews);
                   app.calculate_rating();
                   break;
               }
           }
        });
    }

    app.like_review = function (review_idx) {
        let review = app.vue.reviews[review_idx];

        // no like exists, add it
        if(review.liked == 0) {
            axios.post(
                add_like_url,
                {
                    is_like: true,
                    review: review.id,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.reviews.length; i++) {
                    if(app.vue.reviews[i].id === review.id) {
                        app.vue.reviews[i].liked = 1;
                        app.vue.reviews[i]._like_id = response.data.id;
                        app.vue.reviews[i].likers++;
                        break;
                    }
                }
            });
        }
        // Already liked, unlike
        else if(review.liked == 1) {
            axios.post(
                delete_like_url,
                {id: review._like_id}
            ).then(function (response) {
                for(let i = 0; i < app.vue.reviews.length; i++) {
                    if(app.vue.reviews[i].id === review.id) {
                        app.vue.reviews[i].liked = 0;
                        app.vue.reviews[i]._like_id = -1;
                        app.vue.reviews[i].likers--;
                        break;
                    }
                }
            });
        }
        // Disliked, flip to like
        else {
            axios.post(
                flip_like_url,
                {
                    id: review._like_id,
                    is_like: true,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.reviews.length; i++) {
                    if(app.vue.reviews[i].id === review.id) {
                        app.vue.reviews[i].liked = 1;
                        app.vue.reviews[i].dislikers--;
                        app.vue.reviews[i].likers++;
                        break;
                    }
                }
            });
        }
    }

    app.dislike_review = function (review_idx) {
        let review = app.vue.reviews[review_idx];

        // no like exists, add it
        if(review.liked == 0) {
            axios.post(
                add_like_url,
                {
                    is_like: false,
                    review: review.id,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.reviews.length; i++) {
                    if(app.vue.reviews[i].id === review.id) {
                        app.vue.reviews[i].liked = 2;
                        app.vue.reviews[i]._like_id = response.data.id;
                        app.vue.reviews[i].dislikers++;
                        break;
                    }
                }
            });
        }
        // Already liked, flip to dislike
        else if(review.liked == 1) {
            axios.post(
                flip_like_url,
                {
                    id: review._like_id,
                    is_like: false,
                }
            ).then(function (response) {
                for(let i = 0; i < app.vue.reviews.length; i++) {
                    if(app.vue.reviews[i].id === review.id) {
                        app.vue.reviews[i].liked = 2;
                        app.vue.reviews[i].likers--;
                        app.vue.reviews[i].dislikers++;
                        break;
                    }
                }
            });
        }
        // Already disliked, toggle off
        else {
            axios.post(
                delete_like_url,
                {id: review._like_id}
            ).then(function (response) {
                for(let i = 0; i < app.vue.reviews.length; i++) {
                    if(app.vue.reviews[i].id === review.id) {
                        app.vue.reviews[i].liked = 0;
                        app.vue.reviews[i]._like_id = -1;
                        app.vue.reviews[i].dislikers--;
                        break;
                    }
                }
            });
        }
    }

    app.to_instr = function (rev_idx) {
        let dest = '../instructor/' + app.vue.reviews[rev_idx].instructor.toString();
        window.location.href = dest;
    }

    app.to_course = function (rev_idx) {
        let dest = '../course/' + app.vue.reviews[rev_idx].course.toString();
        window.location.href = dest;
    }

    // This contains all the methods.
    app.methods = {
        //upload_pfp: app.upload_pfp,
        //delete_pfp: app.delete_pfp,
        edit_stars_out: app.edit_stars_out,
        edit_set_star: app.edit_set_star,
        edit_star_over: app.edit_star_over,
        start_edit: app.start_edit,
        save_edit: app.save_edit,
        cancel_edit: app.cancel_edit,
        delete_review: app.delete_review,
        like_review: app.like_review,
        dislike_review: app.dislike_review,
        to_instr: app.to_instr,
        to_course: app.to_course,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#profile-page",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.post(
            load_user_reviews_url,
            {user_id: user_id}
        ).then(function (response) {
            let reviews = response.data.reviews;
            app.enumerate(reviews);
            let likes = response.data.likes;

            for(let i = 0; i < reviews.length; i++) {
                reviews[i].hover = false;
                reviews[i].liked = 0;
                reviews[i]._like_id = -1;
                reviews[i].is_editing = false;
                for(let j = 0; j < likes.length; j++) {
                    if(likes[j].review == reviews[i].id) {
                        reviews[i].liked = likes[j].is_like ? 1 : 2;
                        reviews[i]._like_id = likes[j].id;
                        break;
                    }
                }
            }

            app.vue.reviews = reviews;
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
