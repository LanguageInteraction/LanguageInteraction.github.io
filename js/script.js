(() => {
  const root = document.documentElement;

  const palettes = {
    "Yijun Liu":     ["--yijun1","--yijun2","--yijun3"],
    "Indu Panigrahi":["--indu1","--indu2","--indu3"],
    "Michelle Huang":["--michelle1","--michelle2","--michelle3"],
    "Ziheng (Fred) Huang":["--fred1","--fred2","--fred3"],
    "Sneha Sundar":  ["--sneha1","--sneha2","--sneha3"],
    "Leo Luo":       ["--leo1","--leo2","--leo3"],
    "Yiren Liu":     ["--yiren1","--yiren2","--yiren3"],
    "Lechen Zhang":  ["--lechen1","--lechen2","--lechen3"],
    "Yifan Song":   ["--yifan1","--yifan2","--yifan3"],
    "Tal August":   ["--tal1","--tal2","--tal3"]
  };

  const svg = document.querySelector('#lab-logo svg');

// credit line container
const credit = document.createElement('div');
credit.style.display = 'flex';
credit.style.alignItems = 'center';
const bar = document.createElement('span');
bar.setAttribute('aria-hidden', 'true');
const who = document.createElement('span');
who.className = 'credit-who';

// refresh icon
const icon = document.createElement('span');
icon.textContent = '⟳';
icon.style.cursor = 'pointer';
icon.style.marginLeft = '6px';
icon.title = 'Click to shuffle palette';

// clicking the icon also triggers shuffle
icon.addEventListener('click', () => applyPalette(randomPick(palettes)));

credit.append(bar, who, icon);
svg.after(credit);


  function firstName(full){
    // Prefer nickname in parentheses if present, else first token
    const m = full.match(/\(([^)]+)\)/);
    return m ? m[1].trim() : full.split(/\s+/)[0];
  }

  function creditLine(name){
  const fn = firstName(name);
  who.textContent = (fn === 'Yijun') ? 'Designed by Yijun' : `Color by ${fn}`;
}

function applyPalette(name){
  const [dot, L, bg] = palettes[name];
  const cs = getComputedStyle(root);
  const dotColor = cs.getPropertyValue(dot).trim();
  const LColor   = cs.getPropertyValue(L).trim();
  const bgColor  = cs.getPropertyValue(bg).trim();

  root.style.setProperty('--st1', dotColor);
  root.style.setProperty('--st2', LColor);
  root.style.setProperty('--st3', bgColor);
  svg.style.background = bgColor;

  creditLine(name);
}


function randomPick(obj){
  const keys = Object.keys(obj);
  return keys[(Math.random() * keys.length) | 0];
}

  applyPalette(randomPick(palettes));
  svg.style.cursor = 'pointer';
  svg.title = 'Click to shuffle palette';
  svg.addEventListener('click', () => applyPalette(randomPick(palettes)));
  
})();


document.addEventListener('DOMContentLoaded', function() {
    const track = document.querySelector('.carousel-track');
    const slides = Array.from(track.children);
    const nextButton = document.querySelector('.carousel-btn.next');
    const prevButton = document.querySelector('.carousel-btn.prev');
    const dotsContainer = document.querySelector('.carousel-dots');
    
    let currentIndex = 0;
    
    // Create dots
    slides.forEach((_, index) => {
        const dot = document.createElement('button');
        dot.classList.add('carousel-dot');
        if (index === 0) dot.classList.add('active');
        dot.setAttribute('aria-label', `Go to photo ${index + 1}`);
        dotsContainer.appendChild(dot);
    });
    
    const dots = Array.from(dotsContainer.children);
    
    // Update carousel position
    function updateCarousel(index) {
        track.style.transform = `translateX(-${index * 100}%)`;
        
        // Update dots
        dots.forEach(dot => dot.classList.remove('active'));
        dots[index].classList.add('active');
        
        currentIndex = index;
    }
    
    // Next button
    nextButton.addEventListener('click', () => {
        const nextIndex = (currentIndex + 1) % slides.length;
        updateCarousel(nextIndex);
    });
    
    // Previous button
    prevButton.addEventListener('click', () => {
        const prevIndex = (currentIndex - 1 + slides.length) % slides.length;
        updateCarousel(prevIndex);
    });
    
    // Dot navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            updateCarousel(index);
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            prevButton.click();
        } else if (e.key === 'ArrowRight') {
            nextButton.click();
        }
    });
    
    // Optional: Auto-play (uncomment if desired)
    // setInterval(() => {
    //     nextButton.click();
    // }, 5000); // Change photo every 5 seconds
});

// ---- Section navigation (right-side scroll dots) ----
document.addEventListener('DOMContentLoaded', function () {
    const sections = [
        { id: 'main',         label: 'Home' },
        { id: 'updates',      label: 'Updates' },
        { id: 'blog',         label: 'Blog' },
        { id: 'people',       label: 'People' },
        { id: 'publications', label: 'Publications' },
        { id: 'photo-wall',   label: 'Lab Life' }
    ];

    // Build nav structure
    const nav   = document.createElement('nav');
    nav.className = 'section-nav';
    nav.setAttribute('aria-label', 'Section navigation');

    const track = document.createElement('div');
    track.className = 'section-nav-track';

    // Background line + fill
    const line = document.createElement('div');
    line.className = 'section-nav-line';
    const fill = document.createElement('div');
    fill.className = 'section-nav-line-fill';
    line.appendChild(fill);
    track.appendChild(line);

    // Create dots
    const dots = sections.map(({ id, label }, i) => {
        const btn = document.createElement('button');
        btn.className = 'section-nav-dot' + (i === 0 ? ' active' : '');
        btn.setAttribute('aria-label', 'Go to ' + label);

        const tip = document.createElement('span');
        tip.className = 'nav-tooltip';
        tip.textContent = label;
        btn.appendChild(tip);

        btn.addEventListener('click', () => {
            const el = document.getElementById(id);
            if (el) window.scrollTo({ top: el.offsetTop - 60, behavior: 'smooth' });
        });

        track.appendChild(btn);
        return btn;
    });

    nav.appendChild(track);
    document.body.appendChild(nav);

    // ---- Scroll detection ----
    let active = 0;

    function setActive(idx) {
        if (idx === active) return;
        dots[active].classList.remove('active');
        dots[idx].classList.add('active');
        fill.style.height = (idx / (sections.length - 1) * 100) + '%';
        active = idx;
    }

    function updateNav() {
        const scrollY = window.scrollY;
        let idx = 0;

        for (let i = sections.length - 1; i >= 0; i--) {
            const el = document.getElementById(sections[i].id);
            if (el && el.offsetTop <= scrollY + 75) {
                idx = i;
                break;
            }
        }

        setActive(idx);
    }

    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => { updateNav(); ticking = false; });
            ticking = true;
        }
    });

    updateNav(); // set initial state
});