/**
 * @param {string} selector
 * @returns {HTMLElement | null}
 */
export function findOne(selector) {
  return document.querySelector(selector);
}
/**
 * @param {string} selector
 * @returns {NodeListOf<HTMLElement>}
 */
export function findMany(selector) {
  return document.querySelectorAll(selector);
}
