// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        course_query: "",
        instr_query: "",
        course_is_valid: false,
        instr_is_valid: false,
        courses: [],
        instrs: [],
        course_2_id: {},
        instr_2_id: {},
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // Check if input is a real course
    app.check_course_validity = function () {
        app.vue.course_is_valid = app.vue.course_query in app.vue.course_2_id;
    }

    // Check if input is a real instructor
    app.check_instr_validity = function () {
        app.vue.instr_is_valid = app.vue.instr_query in app.vue.instr_2_id;
    }

    // Navigate to selected course page
    app.course_go = function() {
        let dest = '../course/' + app.vue.course_2_id[app.vue.course_query].toString();
        window.location.href = dest;
    }

    // Navigate to selected instructor page
    app.instr_go = function() {
        let dest = '../instructor/' + app.vue.instr_2_id[app.vue.instr_query].toString();
        window.location.href = dest;
    }

    // This contains all the methods.
    app.methods = {
        check_course_validity: app.check_course_validity,
        check_instr_validity: app.check_instr_validity,
        course_go: app.course_go,
        instr_go: app.instr_go,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#home-page",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.post(
            load_everything_url
        ).then(function(response){
            app.vue.courses = response.data.courses;
            app.vue.instrs = response.data.instrs;
            app.vue.course_2_id = response.data.course_2_id;
            app.vue.instr_2_id = response.data.instr_2_id;
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
