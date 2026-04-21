/* SIDEBAR */
const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("overlay");

menuBtn.onclick = () => {
  sidebar.classList.remove("-translate-x-full");
  overlay.classList.remove("hidden");
};

overlay.onclick = () => {
  sidebar.classList.add("-translate-x-full");
  overlay.classList.add("hidden");
};

/* CATEGORY SLIDER */
const slider = document.getElementById("categorySlider");
const cards = document.querySelectorAll(".cat-card");
const next = document.getElementById("next");
const prev = document.getElementById("prev");
const dotsContainer = document.getElementById("dots");

let index = 0;

/* Create dots */
cards.forEach((_, i) => {
  const dot = document.createElement("div");
  dot.classList.add("dot");
  if (i === 0) dot.classList.add("active");

  dot.onclick = () => moveTo(i);
  dotsContainer.appendChild(dot);
});

const dots = document.querySelectorAll(".dot");

/* Update slider */
function updateSlider() {
  const cardWidth = cards[0].offsetWidth + 16;
  slider.style.transform = `translateX(-${index * cardWidth}px)`;

  dots.forEach(d => d.classList.remove("active"));
  dots[index]?.classList.add("active");
}

/* Move */
function moveTo(i) {
  index = i;
  updateSlider();
}

/* Controls */
next.onclick = () => {
  index = (index + 1) % cards.length;
  updateSlider();
};

prev.onclick = () => {
  index = (index - 1 + cards.length) % cards.length;
  updateSlider();
};

/* Auto Slide */
let auto = setInterval(() => next.click(), 3000);

/* Pause on hover */
slider.addEventListener("mouseenter", () => clearInterval(auto));
slider.addEventListener("mouseleave", () => {
  auto = setInterval(() => next.click(), 3000);
});

/* Swipe */
let startX = 0;

slider.addEventListener("touchstart", e => {
  startX = e.touches[0].clientX;
});

slider.addEventListener("touchend", e => {
  let endX = e.changedTouches[0].clientX;

  if (startX > endX + 50) next.click();
  if (startX < endX - 50) prev.click();
});