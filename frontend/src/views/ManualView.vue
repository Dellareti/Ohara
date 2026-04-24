<template>
  <div class="manual-container">
    <div class="manual-header">
      <h1>User Manual</h1>
      <p>Complete guide to using your manga reader</p>
    </div>

    <div class="manual-content">
      <section id="getting-started" class="manual-section">
        <h2>Getting Started</h2>
        <div class="content-grid">
          <div class="info-card">
            <h3>1. Initial Setup</h3>
            <p>Access <strong>Settings</strong> from the main menu to define your reading and interface preferences.</p>
          </div>
          <div class="info-card">
            <h3>2. Add Manga</h3>
            <p>Use the <strong>Setup</strong> function to add your manga to the system.</p>
          </div>
          <div class="info-card">
            <h3>3. Organization</h3>
            <p>For the system to work properly, keep your folders in the structure indicated in setup. You don't need the same names, just the structure.</p>
          </div>
        </div>
      </section>

      <section id="library" class="manual-section">
        <h2>Library</h2>

        <div class="feature-block">
          <h3>Library Navigation</h3>
          <ul>
            <li><strong>Sorting:</strong> Sort by A-Z, number of chapters, reading progress, or favorites</li>
            <li><strong>Card Size:</strong> Choose between small, medium, or large</li>
            <li><strong>Refresh:</strong> Use the refresh button to reload information from the folder where the manga is located</li>
            <li><strong>Pagination:</strong> Configure how many items to display per page</li>
          </ul>
        </div>

        <div class="feature-block">
          <h3>Manga Details</h3>
          <ul>
            <li>Detailed information (chapters, pages, and progress)</li>
            <li>Full chapter list</li>
            <li>Sorting</li>
            <li>Refresh: Use the refresh button to reload information from the folder where the chapters are located</li>
            <li>Progress: Track your reading progress</li>
            <li>"Continue Reading" option to resume where you left off</li>
          </ul>
        </div>
      </section>

      <section id="reader" class="manual-section">
        <h2>Reader</h2>

        <div class="feature-block">
          <h3>Reading Modes</h3>
          <div class="reading-modes">
            <div class="mode-card">
              <h4>Single Page Mode (horizontal)</h4>
              <p>Displays one page at a time, ideal for traditional manga</p>
            </div>
            <div class="mode-card">
              <h4>Vertical Mode</h4>
              <p>Pages in vertical sequence, perfect for webtoons</p>
            </div>
          </div>
        </div>

        <div class="feature-block">
          <h3>Reader Controls</h3>
          <ul>
            <li><strong>Navigation:</strong> Click the arrows or use the directional keys</li>
            <li><strong>Zoom:</strong> Use the mouse wheel or buttons to zoom</li>
            <li><strong>Fullscreen:</strong> Press F11 or click the fullscreen icon</li>
            <li><strong>Quick Menu:</strong> Click the center of the screen to access controls</li>
          </ul>
        </div>
      </section>

      <section id="settings" class="manual-section">
        <h2>Settings</h2>

        <div class="settings-grid">
          <div class="setting-category">
            <h3>Interface</h3>
            <ul>
              <li>Library card size</li>
              <li>Items per page</li>
              <li>Theme and colors</li>
            </ul>
          </div>

          <div class="setting-category">
            <h3>Reading</h3>
            <ul>
              <li>Default reading mode</li>
              <li>Default reading fit</li>
              <li>Image quality</li>
            </ul>
          </div>

          <div class="setting-category">
            <h3>Performance</h3>
            <ul>
              <li>Image cache</li>
              <li>Page preloading</li>
              <li>Memory optimizations</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="shortcuts" class="manual-section">
        <h2>Keyboard Shortcuts</h2>

        <div class="shortcuts-grid">
          <div class="shortcut-category">
            <h3>General Navigation</h3>
            <div class="shortcut-list">
              <div class="shortcut-item">
              </div>
              <div class="shortcut-item">
                <kbd>Esc</kbd>
                <span>Close modals/menus</span>
              </div>
              <div class="shortcut-item">
                <kbd>Alt + ←</kbd>
                <span>Back</span>
              </div>
            </div>
          </div>

          <div class="shortcut-category">
            <h3>Reader</h3>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>←/→</kbd>
                <span>Previous/Next Page</span>
              </div>
              <div class="shortcut-item">
                <kbd>↑/↓</kbd>
                <span>Scroll Page (Vertical Mode)</span>
              </div>
              <div class="shortcut-item">
                <kbd>h</kbd>
                <span>Open Reader Menu</span>
              </div>
              <div class="shortcut-item">
                <kbd>f</kbd>
                <span>Fullscreen</span>
              </div>
              <div class="shortcut-item">
                <kbd>s</kbd>
                <span>Open Settings Sidebar</span>
              </div>
              <div class="shortcut-item">
                <kbd>Space</kbd>
                <span>Next page</span>
              </div>
            </div>
          </div>

          <div class="shortcut-category">
            <h3>Library</h3>
            <div class="shortcut-list">
              <div class="shortcut-item">
                <kbd>F5</kbd>
                <span>Refresh library</span>
              </div>
              <div class="shortcut-item">
                <kbd>Ctrl + F</kbd>
                <span>Search manga</span>
              </div>
              <div class="shortcut-item">
                <kbd>Enter</kbd>
                <span>Open selected manga</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="tips" class="manual-section">
        <h2>Tips and Tricks</h2>

        <div class="tips-grid">
          <div class="tip-card">
            <h3>Performance</h3>
            <ul>
              <li>Enable image cache for faster loading</li>
              <li>Use preloading on fast connections</li>
            </ul>
          </div>

          <div class="tip-card">
            <h3>Reading</h3>
            <ul>
              <li>Use vertical mode for webtoons and manhwas</li>
              <li>Try different zoom levels for comfort</li>
              <li>The system automatically saves your progress</li>
            </ul>
          </div>

          <div class="tip-card">
            <h3>Organization</h3>
            <ul>
              <li>Sort by reading progress to continue where you left off</li>
              <li>Keep your folders in the correct format (See Setup)</li>
            </ul>
          </div>

          <div class="tip-card">
            <h3>Troubleshooting</h3>
            <ul>
              <li>Clear the cache if images fail to load</li>
              <li>Rescan the library after adding new files</li>
              <li>Check folder permissions if errors occur</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ManualView',
  methods: {
    scrollTo(elementId) {
      const element = document.getElementById(elementId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  },
  mounted() {
    document.title = 'User Manual - Ohara';
  }
}
</script>

<style scoped>
.manual-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  padding: 20px;
}

.manual-header {
  text-align: center;
  margin-bottom: 40px;
}

.manual-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  background: #fff;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.manual-header p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

.manual-content {
  max-width: 1200px;
  margin: 0 auto;
}

.section-nav {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-nav h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.section-nav ul {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.section-nav a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: block;
}

.section-nav a:hover {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
  transform: translateX(5px);
}

.manual-section {
  margin-bottom: 50px;
  scroll-margin-top: 20px;
}

.manual-section h2 {
  font-size: 2rem;
  margin-bottom: 25px;
  color: #fff;
  border-bottom: 2px solid rgba(78, 205, 196, 0.3);
  padding-bottom: 10px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.info-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: translateY(-5px);
}

.info-card h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.feature-block {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-block h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.feature-block ul {
  line-height: 1.8;
}

.feature-block li {
  margin-bottom: 8px;
}

.reading-modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.mode-card {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.mode-card h4 {
  color: #4ecdc4;
  margin-bottom: 10px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
}

.setting-category {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.setting-category h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
}

.shortcut-category {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.shortcut-category h3 {
  color: #4ecdc4;
  margin-bottom: 20px;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.shortcut-item:last-child {
  border-bottom: none;
}

kbd {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
  padding: 4px 8px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.9rem;
  border: 1px solid rgba(78, 205, 196, 0.3);
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
}

.tip-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease;
}

.tip-card:hover {
  transform: translateY(-3px);
}

.tip-card h3 {
  color: #4ecdc4;
  margin-bottom: 15px;
}

.tip-card ul {
  line-height: 1.7;
}

.tip-card li {
  margin-bottom: 8px;
}

.manual-footer {
  text-align: center;
  margin-top: 50px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.manual-footer p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .manual-container {
    padding: 15px;
  }
  
  .manual-header h1 {
    font-size: 2rem;
  }
  
  .manual-section h2 {
    font-size: 1.5rem;
  }
  
  .content-grid,
  .settings-grid,
  .shortcuts-grid,
  .tips-grid {
    grid-template-columns: 1fr;
  }
  
  .section-nav ul {
    grid-template-columns: 1fr;
  }
  
  .reading-modes {
    grid-template-columns: 1fr;
  }
}

/* Smooth animations */
* {
  transition: all 0.3s ease;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(78, 205, 196, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(78, 205, 196, 0.7);
}
</style>