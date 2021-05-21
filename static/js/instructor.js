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
        add_mode: false,
        new_rating: "",
        new_course: "",
        new_body: "",
        author: author,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.set_add_mode = function (new_mode) {
        app.vue.add_mode = new_mode;
    };

    app.reset_form = function () {
        app.vue.new_body = "";
    };

    app.add_review = function () {
        let body = app.vue.new_body;
        axios.post(
            add_review_url,
            {
                course: app.vue.new_course,
                instructor: instr_id,
                body: body,
                rating: parseFloat(app.vue.new_rating),
            }
        ).then(function (response) {
            app.vue.reviews.push({
                _idx: app.vue.reviews.length,
                id: response.data.id,
                body: body,
                course: app.vue.new_course,
                course_name: response.data.course_name,
                instructor: instr_id,
                rating: parseFloat(app.vue.new_rating),
                liked: 0,
                _like_id: -1,
                likers: 0,
                dislikers: 0,
                hover: false,
            })
        });

        app.enumerate(app.vue.reviews);
        app.reset_form();
        app.set_add_mode(false);
    };

    app.cancel_review = function () {
        app.vue.new_body = ""
        app.vue.add_mode = false;
    };

    app.delete_review = function (post_idx) {
        let id = app.vue.reviews[post_idx].id;
        axios.post(
            delete_review_url,
            {id: id}
        ).then(function () {
           for(let i = 0; i < app.vue.reviews.length; i++) {
               if(app.vue.reviews[i].id === id) {
                   app.vue.reviews.splice(i, 1);
                   app.enumerate(app.vue.reviews);
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
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#instr-page",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.post(
            load_instructor_reviews_url,
            {instr_id: instr_id},
        ).then(function (response) {
            let reviews = response.data.reviews;
            app.enumerate(reviews);
            let likes = response.data.likes;

            for(let i = 0; i < reviews.length; i++) {
                reviews[i].hover = false;
                reviews[i].liked = 0;
                reviews[i]._like_id = -1;
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
