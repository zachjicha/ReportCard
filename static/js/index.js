// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        course_query: "",
        is_valid: false,
        results: [],
        courses: [],
        course_2_id: {},
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.search = function () {
        if (app.vue.query.length > 1) {
            axios.get(search_url, {params: {q: app.vue.query}})
                .then(function (result) {
                    app.vue.results = result.data.results;
                });
        } else {
            app.vue.results = [];
        }
    }

    app.check_validity = function () {
        if (app.vue.course_query in app.vue.course_2_id) {
            app.vue.is_valid = true;
        } else {
            app.vue.is_valid = false;
        }
    }

    app.get_go_url = function() {
        location.href = 'course/' + app.vue.course_2_id[app.vue.course_query].toString();
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        search: app.search,
        check_validity: app.check_validity,
        get_go_url: app.get_go_url,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.post(
            load_courses_url
        ).then(function(response){
            app.vue.courses = response.data.courses
            app.vue.course_2_id = response.data.course_2_id
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
