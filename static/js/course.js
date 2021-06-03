// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        reviews: [],
        instructors: [],
        instr_2_id: {},
        add_mode: false,
        is_editing: false,
        edit_text: "",
        edit_stars_displayed: 0,
        edit_rating: 0,
        stars_displayed: 0,
        new_rating: 0,
        new_instr: "",
        new_body: "",
        author: author,
        logged_in: logged_in,
        rating_string: rating_string,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.calculate_rating = function () {
        if(app.vue.reviews.length == 0) {
            app.vue.rating_string = "No reviews yet...";
        }
        else {
            let ratings = 0.0;
            for(let i = 0; i < app.vue.reviews.length; i++) {
                ratings += app.vue.reviews[i].rating;
            }

            let avg_rating = ratings / app.vue.reviews.length;
            app.vue.rating_string = avg_rating.toFixed(1).toString() + "/5.0";
        }
    }

    app.set_add_mode = function (new_mode) {
        app.vue.add_mode = new_mode;
    };

    app.reset_form = function () {
        app.vue.new_body = "";
        app.vue.new_rating = 0;
        app.vue.new_instr = "";
        app.vue.stars_displayed = 0;
    };

    app.stars_out = function () {
        app.vue.stars_displayed = app.vue.new_rating;
    }

    app.set_star = function (star_idx) {
        app.vue.new_rating = star_idx;
    }

    app.star_over = function (star_idx) {
        app.vue.stars_displayed = star_idx;
    }

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

    app.add_review = function () {
        let body = app.vue.new_body;
        axios.post(
            add_review_url,
            {
                course: course_id,
                instructor: app.vue.instr_2_id[app.vue.new_instr],
                body: body,
                rating: parseFloat(app.vue.new_rating),
            }
        ).then(function (response) {
            app.vue.reviews.push({
                id: response.data.id,
                body: body,
                course: course_id,
                course_name: response.data.course_name,
                instructor: app.vue.instr_2_id[app.vue.new_instr],
                instr_name: app.vue.new_instr,
                rating: parseFloat(app.vue.new_rating),
                liked: 0,
                _like_id: -1,
                likers: 0,
                dislikers: 0,
                hover: false,
                user: author,
                is_editing: false,
            });
            app.enumerate(app.vue.reviews);
            app.calculate_rating();
            app.reset_form();
            app.set_add_mode(false);
        });


    };

    app.cancel_review = function () {
        app.vue.new_body = ""
        app.vue.add_mode = false;
    };

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

    app.set_hover = function (post_idx, new_state) {
        app.vue.reviews[post_idx].hover = new_state;
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        set_add_mode: app.set_add_mode,
        add_review: app.add_review,
        cancel_review: app.cancel_review,
        delete_review: app.delete_review,
        like_review: app.like_review,
        dislike_review: app.dislike_review,
        set_hover: app.set_hover,
        star_over: app.star_over,
        stars_out: app.stars_out,
        set_star: app.set_star,
        start_edit: app.start_edit,
        save_edit: app.save_edit,
        cancel_edit: app.cancel_edit,
        edit_star_over: app.edit_star_over,
        edit_stars_out: app.edit_stars_out,
        edit_set_star: app.edit_set_star,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#course-page",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.post(
            load_course_reviews_url,
            {course_id: course_id},
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

            app.vue.instructors = response.data.instructors;
            app.vue.instr_2_id = response.data.instr_2_id;
            app.vue.reviews = reviews;
            app.calculate_rating();
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
