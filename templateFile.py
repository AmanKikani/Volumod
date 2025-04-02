import streamlit as st


config = {
    "toImageButtonOptions": {
        "format": "png",
        "filename": "custom_image",
        "height": 720,
        "width": 480,
        "scale": 6,
    }
}


particles_js = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Particles.js</title>
  <style>
  #particles-js {
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: -1; /* Send the animation to the back */
  }
  .content {
    position: relative;
    z-index: 1;
    color: white;
  }

</style>
</head>
<body>
  <div id="particles-js"></div>
  <div class="content">
    <!-- Placeholder for Streamlit content -->
  </div>
  <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
  <script>
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 300,
          "density": {
            "enable": true,
            "value_area": 800
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#000000"
          },
          "polygon": {
            "nb_sides": 5
          },
          "image": {
            "src": "img/github.svg",
            "width": 100,
            "height": 100
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.2,
            "sync": false
          }
        },
        "size": {
          "value": 2,
          "random": true,
          "anim": {
            "enable": false,
            "speed": 40,
            "size_min": 0.1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#ffffff",
          "opacity": 0.22,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 0.2,
          "direction": "none",
          "random": false,
          "straight": false,
          "out_mode": "out",
          "bounce": true,
          "attract": {
            "enable": false,
            "rotateX": 600,
            "rotateY": 1200
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": true,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 2,
            "duration": 2,
            "opacity": 0.5,
            "speed": 1
          },
          "repulse": {
            "distance": 200,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 2
          },
          "remove": {
            "particles_nb": 3
          }
        }
      },
      "retina_detect": true
    });
  </script>
</body>
</html>
"""

st.set_page_config(page_title="Volumod.net", page_icon="🔊", layout="wide")
st.title("Welcome to Volumod.net")
components.html(particles_js, height=700, scrolling=False)
st.sidebar.caption(
    "Built by Aman Kikani. Connect with me on [LinkedIn](https://www.linkedin.com/in/aman-kikani-466716269/)."
)

linkedin = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/linkedin.gif"
topmate = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/topmate.gif"
email = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/email.gif"
newsletter = (
    "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/newsletter.gif"
)
share = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/share.gif"

uptime = "https://uptime.betterstack.com/status-badges/v1/monitor/196o6.svg"

st.sidebar.caption(
    f"""
        <div style='display: flex; align-items: center;'>
            <a href = 'https://www.linkedin.com/in/sahir-maharaj/'><img src='{linkedin}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
            <a href = 'https://topmate.io/sahirmaharaj/362667'><img src='{topmate}' style='width: 32px; height: 32px; margin-right: 25px;'></a>
            <a href = 'mailto:sahir@sahirmaharaj.com'><img src='{email}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
            <a href = 'https://www.linkedin.com/build-relation/newsletter-follow?entityUrn=7163516439096733696'><img src='{newsletter}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
            <a href = 'https://www.kaggle.com/sahirmaharajj'><img src='{share}' style='width: 28px; height: 28px; margin-right: 25px;'></a>

        </div>
        <br>
        <a href = 'https://exifa.betteruptime.com/'><img src='{uptime}'></a>
        &nbsp; <a href="https://www.producthunt.com/posts/exifa-net?embed=true&utm_source=badge-featured&utm_medium=badge&utm_souce=badge-exifa&#0045;net" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=474560&theme=dark" alt="Exifa&#0046;net - Your&#0032;AI&#0032;assistant&#0032;for&#0032;understanding&#0032;EXIF&#0032;data | Product Hunt" style="width: 125px; height: 27px;" width="125" height="27" /></a>

        """,
    unsafe_allow_html=True,
)
prompt = st.chat_input("Hello! How can I assist you today?")
if prompt != None:
    st.write("You: ", prompt)

st.button("Submit")

