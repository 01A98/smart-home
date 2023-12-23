import { findOne } from "./utils.js";

export const SELECTORS = {
  NAVBAR_MENU_TOGGLE: "#mobile-menu-toggle",
  NAVBAR_MENU_ITEMS_LIST: "ul#menu-items",
  OPEN_MENU_ICON: "svg#open-menu",
  CLOSE_MENU_ICON: "svg#close-menu",
};

export const NAVBAR_TAB_HIGHLIGHT_CLASSLIST = [
  "bg-blue-700",
  "dark:text-white",
  "md:text-blue-700",
  "md:dark:text-blue-500",
];

/**
 * @param {CustomEvent} evt The `navigating-to-page` event with `detail.value` and `detail.elt` present.
 * @returns {void}
 */
export function handleNavbarHighlighting(evt) {
  const navBarMenuItemsList = findOne(SELECTORS.NAVBAR_MENU_ITEMS_LIST);

  if (navBarMenuItemsList) {
    const anchorTags = navBarMenuItemsList.querySelectorAll("a");

    anchorTags.forEach((a) => {
      if (a.dataset.pageName === evt.detail.value) {
        a.classList.add(...NAVBAR_TAB_HIGHLIGHT_CLASSLIST);
      } else {
        a.classList.remove(...NAVBAR_TAB_HIGHLIGHT_CLASSLIST);
      }
    });
  }
}

/**
 * Main entry point for common code to be executed on every page inheriting from base.html template.
 * @returns {void}
 */
function main() {
  // @ts-ignore
  document.body.addEventListener(
    "navigating-to-page",
    handleNavbarHighlighting
  );
}

main();
