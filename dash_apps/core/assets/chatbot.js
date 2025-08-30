// Simple chatbot drag functionality
(function() {
  console.log('[chatbot] Script loaded');
  
  let isDragging = false;
  let dragElement = null;
  let startX, startY, startLeft, startTop;

  function makeDraggable(element, handle) {
    if (!element || !handle) return;
    
    handle.addEventListener('mousedown', function(e) {
      if (e.target.closest('button')) return;
      
      isDragging = true;
      dragElement = element;
      
      startX = e.clientX;
      startY = e.clientY;
      
      const rect = element.getBoundingClientRect();
      startLeft = rect.left;
      startTop = rect.top;
      
      element.style.position = 'fixed';
      element.style.left = startLeft + 'px';
      element.style.top = startTop + 'px';
      element.style.right = 'auto';
      element.style.bottom = 'auto';
      
      document.addEventListener('mousemove', onDragMove);
      document.addEventListener('mouseup', onDragUp);
      e.preventDefault();
    });
  }
  
  function onDragMove(e) {
    if (!isDragging || !dragElement) return;
    
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    
    const newLeft = Math.max(0, Math.min(startLeft + dx, window.innerWidth - dragElement.offsetWidth));
    const newTop = Math.max(0, Math.min(startTop + dy, window.innerHeight - dragElement.offsetHeight));
    
    dragElement.style.left = newLeft + 'px';
    dragElement.style.top = newTop + 'px';
  }
  
  function onDragUp() {
    isDragging = false;
    dragElement = null;
    document.removeEventListener('mousemove', onDragMove);
    document.removeEventListener('mouseup', onDragUp);
  }
  
  function makeResizable(element) {
    if (!element) return;
    
    const resizer = element.querySelector('.chatbot-resizer');
    if (!resizer) return;
    
    console.log('[chatbot] Making element resizable:', element.className);
    
    let isResizing = false;
    let startX, startY, startWidth, startHeight;
    
    resizer.addEventListener('mousedown', function(e) {
      console.log('[chatbot] Resize start');
      isResizing = true;
      
      startX = e.clientX;
      startY = e.clientY;
      startWidth = parseInt(document.defaultView.getComputedStyle(element).width, 10);
      startHeight = parseInt(document.defaultView.getComputedStyle(element).height, 10);
      
      // Add event listeners to document and window to catch all mouse events
      document.addEventListener('mousemove', onResizeMove, { capture: true, passive: false });
      document.addEventListener('mouseup', onResizeUp, { capture: true, passive: false });
      window.addEventListener('mousemove', onResizeMove, { capture: true, passive: false });
      window.addEventListener('mouseup', onResizeUp, { capture: true, passive: false });
      
      // Prevent default and stop propagation
      e.preventDefault();
      e.stopPropagation();
      
      // Add visual feedback
      document.body.style.cursor = 'se-resize';
      document.body.style.userSelect = 'none';
    });
    
    function onResizeMove(e) {
      if (!isResizing) return;
      
      // Prevent default to avoid text selection and other browser behaviors
      e.preventDefault();
      e.stopPropagation();
      
      // Simple resize from bottom-right corner (no position changes)
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      
      const newWidth = startWidth + deltaX;
      const newHeight = startHeight + deltaY;
      
      // Set minimum and maximum sizes
      const minWidth = 300;
      const minHeight = 200;
      const maxWidth = window.innerWidth * 0.9;
      const maxHeight = window.innerHeight * 0.9;
      
      const finalWidth = Math.max(minWidth, Math.min(newWidth, maxWidth));
      const finalHeight = Math.max(minHeight, Math.min(newHeight, maxHeight));
      
      // Only resize, don't move the container at all
      element.style.width = finalWidth + 'px';
      element.style.height = finalHeight + 'px';
    }
    
    function onResizeUp(e) {
      console.log('[chatbot] Resize end');
      
      // Immediately stop resizing
      isResizing = false;
      
      // Remove all event listeners immediately
      document.removeEventListener('mousemove', onResizeMove, { capture: true });
      document.removeEventListener('mouseup', onResizeUp, { capture: true });
      window.removeEventListener('mousemove', onResizeMove, { capture: true });
      window.removeEventListener('mouseup', onResizeUp, { capture: true });
      
      // Reset cursor and selection immediately
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      
      // Prevent any further event propagation
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
    }
  }

  function initDrag() {
    console.log('[chatbot] Init drag');
    
    // Make bubble draggable
    const bubble = document.getElementById('open-chatbot-bubble');
    if (bubble) {
      console.log('[chatbot] Found bubble');
      makeDraggable(bubble, bubble);
    }
    
    // Make window draggable and resizable
    const window = document.getElementById('chatbot-window');
    const windowInner = window ? window.querySelector('.chatbot-window-inner') : null;
    const dragger = windowInner ? windowInner.querySelector('.chatbot-header.chatbot-dragger') : null;
    const resizer = windowInner ? windowInner.querySelector('.chatbot-resizer') : null;
    
    console.log('[chatbot] Elements found:', { 
      window: !!window, 
      windowInner: !!windowInner,
      dragger: !!dragger, 
      resizer: !!resizer 
    });
    
    if (window && dragger) {
      console.log('[chatbot] Making window draggable');
      makeDraggable(window, dragger);
    }
    
    if (windowInner && resizer) {
      console.log('[chatbot] Making window resizable');
      makeResizable(windowInner);
    }
  }
  
  // Initialize multiple times to catch Dash updates
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDrag);
  } else {
    initDrag();
  }
  
  // Try again after a short delay for Dash
  setTimeout(initDrag, 1000);
  setTimeout(initDrag, 3000);
  
})();
