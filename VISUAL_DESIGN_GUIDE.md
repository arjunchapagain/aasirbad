# Aasirbad Homepage - Visual Design & Interaction Guide
## Mockups, Flows, and Interaction Patterns

---

## 🎨 HOMEPAGE VISUAL LAYOUT

```
┌─────────────────────────────────────────────────┐
│                 NAVIGATION BAR                  │  Height: 80px
│  Logo | Language Toggle | Sign In | Get Started │
├─────────────────────────────────────────────────┤
│                                                 │
│              HERO SECTION                       │  Height: 100vh
│         (Full Screen, Background Image)         │
│                                                 │
│     The Voices We Love, Forever                 │  Headline
│                                                 │
│    [Subheading text here...]                    │  Subheading
│                                                 │
│    ✓ Free ✓ Your data ✓ Secure                 │  Trust badges
│                                                 │
│    [Start Recording Free] [See How It Works →]  │  CTAs
│                                                 │
├─────────────────────────────────────────────────┤
│          WHAT IS AASIRBAD SECTION               │  Padding: 80px
│   [Card] [Card] [Card]                          │
│  Benefits in 3 columns (mobile: stacked)        │
├─────────────────────────────────────────────────┤
│           HOW IT WORKS SECTION                  │  Padding: 80px
│  Step 1 → Step 2 → Step 3                       │  3-column grid
│  [Card]  [Card]  [Card]                         │
├─────────────────────────────────────────────────┤
│             USE CASES SECTION                   │  Padding: 80px
│  [Card] [Card]                                  │  2-column grid
│  [Card] [Card]                                  │  (or stacked on mobile)
├─────────────────────────────────────────────────┤
│         TRUST & PRIVACY SECTION                 │  Padding: 80px
│  [Pillar] [Pillar]                              │  2x2 grid
│  [Pillar] [Pillar]                              │
├─────────────────────────────────────────────────┤
│                FAQ SECTION                      │  Padding: 80px
│  [Question ▼]                                   │  Accordion
│  [Answer appears below]                         │
│  [Question ▼]                                   │
│  [Question ▼]                                   │
├─────────────────────────────────────────────────┤
│            FINAL CTA SECTION                    │  Padding: 80px
│         (Dark background color)                 │
│                                                 │
│  Your Family's Voice Deserves to Last Forever   │
│     [Record First Story Free] [Watch Demo]      │
│                                                 │
│  ⭐ 4.8/5 | ✓ 15 countries | ✓ 50K recordings  │
│                                                 │
├─────────────────────────────────────────────────┤
│                   FOOTER                        │  Padding: 40px
│  Copyright | Privacy | Terms | Contact | Social │
└─────────────────────────────────────────────────┘
```

---

## 📱 MOBILE LAYOUT CHANGES

### Hero Section (Mobile)
```
┌──────────────────┐
│    HERO MOBILE   │  Height: 70vh
│  (Background     │  Font sizes smaller
│   image visible  │  Padding reduced
│   but smaller)   │
│                  │
│  The Voices We   │  Headline: 32px (vs 56px desktop)
│  Love, Forever   │
│                  │
│  [Subheading     │  Subheading: 16px
│   text...]       │  (max 2-3 lines)
│                  │
│  ✓ Free          │  Stacked trust badges
│  ✓ Your data     │  (vertical)
│  ✓ Secure        │
│                  │
│  [Button Full    │  Full-width buttons
│   Width]         │  Stacked vertically
│  [Button Full    │
│   Width]         │
└──────────────────┘
```

### Sections (Mobile)
- Cards: Stack to 1 column
- Padding: Reduce from 80px to 40px
- Font: Slightly larger for readability
- Images: Full-width, optimized for mobile

---

## 🎯 HERO SECTION DETAILED MOCKUP

```
┌─────────────────────────────────────────────────┐
│                   NAV (Fixed)                    │
│  🏠 Aasirbad  |  [English ▼]  [Sign In] [Start] │
├─────────────────────────────────────────────────┤
│                                                 │
│                                                 │
│   [Background Image: Family & Grandparent]      │
│   [Semi-dark overlay: rgba(0,0,0,0.3)]          │
│                                                 │
│                                                 │
│              ←← TEXT OVERLAY →→                 │
│                                                 │
│              The Voices We Love,                │  Color: #2C2C2C
│                   Forever                       │  Font: Serif, Bold
│              (56px on desktop)                  │  Line height: 1.2
│                                                 │
│        Preserve your parents' blessings,       │  Color: #4A4A4A
│     grandparents' stories, and family wisdom   │  Font: Sans, Regular
│    in their own voice. Never lose that precious│  (18px, max 60 chars/line)
│           sound again.                          │
│                                                 │
│              ✓ Free to start                    │  Color: #666
│              ✓ Your voice, your data            │  Font: Sans, Regular (14px)
│              ✓ Private & secure                 │
│              (Horizontal on desktop,            │  Stacked on mobile
│               Stacked on mobile)                │
│                                                 │
│         [Start Recording Free]                  │  Primary CTA
│         BG: #8B6F47, Text: White                │  Padding: 16px 32px
│         Hover: BG: #6F5A37                      │  Border radius: 8px
│                                                 │
│         [See How It Works →]                    │  Secondary CTA
│         BG: White, Text: #8B6F47                │  Border: 2px
│         Hover: BG: #F8F6F1                      │
│                                                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 💳 CARD COMPONENT DESIGN

### Benefit Card (What is Aasirbad)
```
┌─────────────────────┐
│                     │
│       🎤            │  Icon: 48px, color: #D4A574
│                     │
│  Simple Recording   │  Title: 24px, Bold, #2C2C2C
│                     │
│  No technical skills│  Description: 16px, regular, #666
│  needed. Record on  │  (2-3 lines max)
│  any device—phone,  │
│  tablet, or         │
│  computer. One      │
│  click. That's it.  │
│                     │
│  Designed for all   │  Badge: 12px, italic, #999
│                     │
└─────────────────────┘
Hover: Shadow deepens, slight scale up
```

### Use Case Card
```
┌──────────────────────────┐
│                          │
│  A Grandmother's         │  Title: 20px, Bold
│  Blessings for Life      │  Color: #2C2C2C
│                          │
│  Meena's grandmother... │  Story text: 14px, #666
│  [Full story...]        │  Line height: 1.6
│                          │
│  ┌────────────────────┐  │
│  │ 🎯 Result:        │  │  Callout box:
│  │ A family tradition │  │  BG: #D4A574/5%
│  │ preserved. A voice │  │  Border-left: 4px #D4A574
│  │ that lasts forever.│  │  Padding: 16px
│  └────────────────────┘  │
│                          │
└──────────────────────────┘
Left border: 4px #C9989A (on hover or as accent)
```

### FAQ Item (Closed)
```
┌────────────────────────────────────┐
│ Who can use Aasirbad?        [↓]   │  BG: White
│                                    │  Border: 1px #E0E0E0
└────────────────────────────────────┘  Padding: 24px
Hover: BG: #F8F6F1
```

### FAQ Item (Open)
```
┌────────────────────────────────────┐
│ Who can use Aasirbad?        [↑]   │  (rotated icon)
├────────────────────────────────────┤
│                                    │  Divider line
│ Anyone who wants to preserve...    │
│ [Full answer text...]             │  BG: #F8F6F1
│                                    │  Padding: 24px
└────────────────────────────────────┘
Smooth animation (0.3s) on height change
```

---

## 🎬 INTERACTION PATTERNS

### CTA Button States

```
DEFAULT STATE
┌──────────────────────────┐
│ Start Recording Free     │  BG: #8B6F47
└──────────────────────────┘  Color: White
                               Font-weight: 600

HOVER STATE
┌──────────────────────────┐
│ Start Recording Free     │  BG: #6F5A37 (darker)
└──────────────────────────┘  Cursor: pointer
                               Box-shadow: 0 4px 12px rgba(0,0,0,0.15)
                               Transform: scale(1.02)

ACTIVE STATE
┌──────────────────────────┐
│ Start Recording Free     │  BG: #5C4A2E (even darker)
└──────────────────────────┘  Transform: scale(0.98)

DISABLED STATE
┌──────────────────────────┐
│ Start Recording Free     │  BG: #CCCCCC
└──────────────────────────┘  Opacity: 0.6
                               Cursor: not-allowed
```

### FAQ Accordion Animation
```
BEFORE CLICK: [Question ▼]

ON CLICK: Smooth expand
- Duration: 300ms
- Easing: ease-in-out
- Icon rotates: 0° → 180°
- Height: auto
- Content fades in

AFTER: [Question ▲]
       [Answer text visible]

ON SECOND CLICK: Smooth collapse
- Reverse animation
```

### Hover Effects (Cards)
```
DEFAULT:
Box-shadow: 0 2px 8px rgba(0,0,0,0.08)
Transform: translateY(0)

HOVER:
Box-shadow: 0 8px 24px rgba(0,0,0,0.12)
Transform: translateY(-4px)
Transition: all 200ms ease-out
```

---

## 🌍 RESPONSIVE BREAKPOINTS

### Desktop (1024px and up)
- 3-column grids (benefits, how it works front)
- 2-column grids (use cases, trust pillars)
- Full-width sections with max-width wrapper
- Hover states active

### Tablet (768px - 1023px)
- 2-column grids → 2 columns (still fit nicely)
- Padding reduces to 60px
- Font sizes slightly smaller
- Hero: 80vh height

### Mobile (480px - 767px)
- Single column layout
- Padding: 40px
- Hero: 70vh height (or 80vh if short)
- All grids become single column
- Buttons: full-width
- Dropdowns/menus: mobile-optimized

### Small Mobile (< 480px)
- Padding: 20px
- Font sizes minimum 14px body
- Hero: 60vh or even less
- Images: critical optimization
- Buttons: large touch targets (44x44px)

---

## 🎨 COLOR USAGE GUIDE

### Primary Color: Warm Brown (#8B6F47)
- Main CTA buttons
- Section accents
- Links (hover state)
- Text highlights

### Secondary Color: Warm Gold (#D4A574)
- Icon backgrounds
- Accent lines
- Badges and tags
- Highlights on cards

### Tertiary Color: Soft Teal (#6B9BD1)
- Secondary actions (if needed)
- Links (default)
- Hover states (alternatives)

### Accent Color: Soft Rose (#C9989A)
- Left borders on use case cards
- Emotional emphasis
- Highlight boxes
- Visual breaks

### Neutrals:
- Deep Charcoal (#2C2C2C): Headlines, primary text
- Gray (#666666): Secondary text, descriptions
- Light Gray (#CCCCCC): Borders, dividers
- Warm White (#F8F6F1): Backgrounds, hover states

---

## 📐 SPACING & SIZING SYSTEM

### Spacing Scale (Tailwind-based)
```
4px   = 1 unit
8px   = 2 units
12px  = 3 units
16px  = 4 units (base)
24px  = 6 units
32px  = 8 units
40px  = 10 units (section padding mobile)
48px  = 12 units
80px  = 20 units (section padding desktop)
```

### Button Sizes
```
Small:
Height: 36px
Padding: 12px 24px
Font: 14px

Default:
Height: 44px
Padding: 16px 32px
Font: 16px

Large:
Height: 52px
Padding: 18px 40px
Font: 18px
```

### Font Sizes
```
Hero Headline: 56px (desktop), 32px (mobile)
Section Headline: 40px (desktop), 28px (mobile)
Subheading: 18px (desktop), 16px (mobile)
Body: 16px (desktop), 14px (mobile)
Small text: 14px (desktop), 12px (mobile)
```

---

## 🎯 VISUAL HIERARCHY

### Prominence Levels

**Level 1: Hero Headline**
- Size: Largest (56px desktop)
- Weight: Bold
- Color: Deep charcoal (#2C2C2C)
- Purpose: First thing seen, main message

**Level 2: Section Headlines + Primary CTA**
- Size: Large (40px headlines, 16px buttons)
- Weight: Bold for headlines, semi-bold for buttons
- Color: Deep charcoal for text, warm brown for buttons
- Purpose: Guide reader through page, drive action

**Level 3: Subheadings + Card Titles**
- Size: Medium (18px, 24px)
- Weight: Semi-bold
- Color: Deep charcoal or secondary gray
- Purpose: Structure content, create scanning path

**Level 4: Body Text + Secondary CTA**
- Size: Base (16px)
- Weight: Regular
- Color: Gray (#666)
- Purpose: Detailed information, secondary actions

**Level 5: Supporting Text**
- Size: Small (12-14px)
- Weight: Regular or Light
- Color: Light gray
- Purpose: Captions, badges, helper text

---

## ♿ ACCESSIBILITY DESIGN

### Color Contrast
- All text: Minimum 4.5:1 for body, 3:1 for large text
- Links: Underlined or different color + additional indicator
- Buttons: Not relying on color alone to convey status

### Interactive Elements
- Minimum touch target: 44x44px
- Clear focus states (ring or outline)
- Keyboard navigation: Tab order visible and logical
- Skip navigation link at top (hidden until focused)

### Text Readability
- Line length: Max 75 characters
- Line height: Minimum 1.5 (1.6+ for body)
- Font size: Minimum 14px (16px for body)
- Spacing between paragraphs: Clear visual separation

### Images
- All decorative images: role="presentation" or aria-hidden="true"
- All meaningful images: Descriptive alt text
- SVG icons: aria-label or <title> element

---

## 📸 IMAGE SPECIFICATIONS

### Hero Background Image
- Size: 1920px × 1080px (min)
- Format: WebP (primary), JPG (fallback)
- Compression: 60-80KB
- Content: Multigenerational family, warm lighting
- Overlay: Transparent black (30% opacity)

### Section Images/Icons
- Size: 200px × 200px (cards)
- Format: SVG (preferred) or PNG with transparency
- Style: Hand-drawn, warm colors
- Consistency: Unified style across all icons

### Testimonial/Case Study Images
- Size: 400px × 400px (min)
- Format: JPG (compressed)
- Size: 60-100KB per image
- Style: Authentic photos, real people
- Diversity: Represent target audience

### Optimization
- Use Next.js Image component (automatic optimization)
- Lazy loading for below-fold images
- Srcset for different device sizes
- Format: Prefer WebP with JPG fallback

---

## ⚡ PERFORMANCE TARGETS

### Core Web Vitals
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms
- **CLS (Cumulative Layout Shift):** < 0.1

### Page Load Metrics
- Total Size: < 500KB (gzipped)
- Time to Interactive: < 3.5s
- First Contentful Paint: < 1.2s
- Lighthouse Score: 90+

### Optimization Techniques
- Image optimization (WebP, lazy loading)
- CSS minification and critical CSS inline
- JavaScript code splitting
- Font optimization (system fonts or optimized web fonts)
- Caching strategy (static assets: 1 year, dynamic: 1 hour)

---

## 🌙 DARK MODE (Optional Future)

If you want to add dark mode:

```
Light Mode (Current)
Background: #F8F6F1
Text: #2C2C2C
Cards: #FFFFFF
Accents: #D4A574

Dark Mode (Future)
Background: #1A1A1A
Text: #E8E8E8
Cards: #2A2A2A
Accents: #D4A574 (maintains warmth)
```

---

## ✅ DESIGN SYSTEM CHECKLIST

- [ ] Color palette defined in Figma/design tool
- [ ] Typography scale locked (6-8 sizes max)
- [ ] Spacing/sizing system created
- [ ] Button component states defined
- [ ] Card components designed (3+ types)
- [ ] Responsive breakpoints set
- [ ] Hover/active/focus states for all interactive elements
- [ ] Accessibility guidelines documented
- [ ] Image specifications written
- [ ] Animations/transitions defined
- [ ] Loading states designed
- [ ] Error/validation states designed
- [ ] Component library created (if using design tool)

---

**Visual consistency + smooth interactions + accessibility = Professional homepage that converts.**

