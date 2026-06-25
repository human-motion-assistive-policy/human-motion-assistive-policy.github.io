window.HELP_IMPROVE_VIDEOJS = false;

var INTERP_BASE = "https://homes.cs.washington.edu/~kpar/nerfies/interpolation/stacked";
var NUM_INTERP_FRAMES = 240;

var interp_images = [];
function preloadInterpolationImages() {
  for (var i = 0; i < NUM_INTERP_FRAMES; i++) {
    var path = INTERP_BASE + '/' + String(i).padStart(6, '0') + '.jpg';
    interp_images[i] = new Image();
    interp_images[i].src = path;
  }
}

function setInterpolationImage(i) {
  var image = interp_images[i];
  image.ondragstart = function() { return false; };
  image.oncontextmenu = function() { return false; };
  $('#interpolation-image-wrapper').empty().append(image);
}


$(document).ready(function() {
    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function() {
      // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
      $(".navbar-burger").toggleClass("is-active");
      $(".navbar-menu").toggleClass("is-active");

    });

    var options = {
			slidesToScroll: 1,
			slidesToShow: 3,
			loop: true,
			infinite: true,
			autoplay: false,
			autoplaySpeed: 3000,
    }

		// Initialize all div with carousel class
    var carousels = bulmaCarousel.attach('.carousel', options);

    // Loop on each carousel initialized
    for(var i = 0; i < carousels.length; i++) {
    	// Add listener to  event
    	carousels[i].on('before:show', state => {
    		console.log(state);
    	});
    }

    // Access to bulmaCarousel instance of an element
    var element = document.querySelector('#my-element');
    if (element && element.bulmaCarousel) {
    	// bulmaCarousel instance is available as element.bulmaCarousel
    	element.bulmaCarousel.on('before-show', function(state) {
    		console.log(state);
    	});
    }

    preloadInterpolationImages();

    $('#interpolation-slider').on('input', function(event) {
      setInterpolationImage(this.value);
    });
    setInterpolationImage(0);
    $('#interpolation-slider').prop('max', NUM_INTERP_FRAMES - 1);

    bulmaSlider.attach();

    var singleTaskVideo = document.getElementById("single-task-result-video");
    var multiTaskVideo = document.getElementById("multi-task-result-video");
    if (singleTaskVideo) {
      singleTaskVideo.playbackRate = 2.0;
    }
    if (multiTaskVideo) {
      multiTaskVideo.playbackRate = 2.0;
    }

    var dataCurationVideos = Array.from(document.querySelectorAll(".data-curation-video video"));
    if (dataCurationVideos.length) {
      var restartDataCurationVideos = function() {
        dataCurationVideos.forEach(function(video) {
          video.currentTime = 0;
        });
        dataCurationVideos.forEach(function(video) {
          var playPromise = video.play();
          if (playPromise && playPromise.catch) {
            playPromise.catch(function() {});
          }
        });
      };

      Promise.all(dataCurationVideos.map(function(video) {
        video.muted = true;
        video.loop = false;
        video.currentTime = 0;

        return new Promise(function(resolve) {
          if (video.readyState >= 2) {
            resolve();
          } else {
            video.addEventListener("loadeddata", resolve, { once: true });
            video.addEventListener("error", resolve, { once: true });
          }
        });
      })).then(function() {
        restartDataCurationVideos();
      });

      var restartTimer = null;
      dataCurationVideos.forEach(function(video) {
        video.addEventListener("ended", function() {
          if (restartTimer) {
            return;
          }
          restartTimer = window.setTimeout(function() {
            restartTimer = null;
            restartDataCurationVideos();
          }, 2500);
        });
      });
    }

    var policyComparisonVideos = Array.from(document.querySelectorAll(".policy-comparison-grid video"));
    if (policyComparisonVideos.length) {
      var policyComparisonRows = [];
      for (var rowStart = 0; rowStart < policyComparisonVideos.length; rowStart += 2) {
        policyComparisonRows.push(policyComparisonVideos.slice(rowStart, rowStart + 2));
      }

      var playTogether = function(rowVideos) {
        rowVideos.forEach(function(video) {
          video.loop = false;
          video.currentTime = 0;
        });
        rowVideos.forEach(function(video) {
          var playPromise = video.play();
          if (playPromise && playPromise.catch) {
            playPromise.catch(function() {});
          }
        });
      };

      policyComparisonRows.forEach(function(rowVideos) {
        Promise.all(rowVideos.map(function(video) {
          video.muted = true;
          video.loop = false;
          return new Promise(function(resolve) {
            if (video.readyState >= 2) {
              resolve();
            } else {
              video.addEventListener("loadeddata", resolve, { once: true });
              video.addEventListener("error", resolve, { once: true });
            }
          });
        })).then(function() {
          playTogether(rowVideos);
        });

        rowVideos.forEach(function(video) {
          video.addEventListener("ended", function() {
            if (rowVideos.every(function(rowVideo) { return rowVideo.ended; })) {
              window.setTimeout(function() {
                playTogether(rowVideos);
              }, 100);
            }
          });

          video.addEventListener("timeupdate", function() {
            var reference = rowVideos[0];
            if (!reference || reference.paused || video === reference) {
              return;
            }
            if (Math.abs(video.currentTime - reference.currentTime) > 0.2) {
              video.currentTime = reference.currentTime;
            }
          });
        });
      });
    }

    var bodyScaleVideos = Array.from(document.querySelectorAll(".body-scale-grid video"));
    if (bodyScaleVideos.length) {
      bodyScaleVideos.forEach(function(video) {
        var restartTimer = null;
        var restartDelay = Number(video.getAttribute("data-restart-delay") || 2000);
        video.loop = false;
        video.muted = true;

        var restartBodyScaleVideo = function() {
          restartTimer = null;
          video.currentTime = 0;
          var playPromise = video.play();
          if (playPromise && playPromise.catch) {
            playPromise.catch(function() {});
          }
        };

        video.addEventListener("ended", function() {
          if (restartTimer) {
            return;
          }
          restartTimer = window.setTimeout(restartBodyScaleVideo, restartDelay);
        });
      });
    }
})
