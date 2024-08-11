from dominate.tags import ul, p, button, a

from src.components.material_icons import Icon


class CrudOptionsMenu(Icon):
    tagname = "span"

    def __init__(
        self,
        icon_name: str,
        hx_delete: str,
        edit_page_url: str,
        delete_text: str,
        edit_text: str,
        **kwargs,
    ) -> None:
        super().__init__(
            icon_name,
            class_name="self-end px-4 pb-2 relative text-[42px] inline-block cursor-pointer material-icons-round",
            **{
                "x-data": "{ open: false }",
                "@click": "open = !open",
                "@click.outside": "open = false",
                **kwargs,
            },
        )
        with self:
            with ul(
                role="menu",
                data_popover_placement="left",
                class_name="absolute z-10 -top-28 right-3 flex min-w-[180px] flex-col gap-2 overflow-auto rounded-md "
                "border border-blue-gray-50 bg-white p-3 font-sans text-sm font-normal text-blue-gray-500 "
                "shadow-lg shadow-blue-gray-500/10 focus:outline-none",
                **{
                    "x-show": "open",
                    "x-transition:enter": "transition ease-out duration-200",
                    "x-transition:enter-start": "opacity-0 scale-90",
                    "x-transition:enter-end": "opacity-100 scale-100",
                    "x-transition:leave": "transition ease-in duration-200",
                    "x-transition:leave-start": "opacity-100 scale-100",
                    "x-transition:leave-end": "opacity-0 scale-90",
                },
            ):
                with button(
                    role="menuitem",
                    class_name="flex w-full cursor-pointer select-none items-center gap-2 rounded-md px-3 pt-[9px] "
                    "pb-2 text-start leading-tight outline-none transition-all hover:bg-blue-gray-50 "
                    "hover:bg-opacity-80 hover:text-blue-gray-900 focus:bg-blue-gray-50 "
                    "focus:bg-opacity-80 focus:text-blue-gray-900 active:bg-blue-gray-50 "
                    "active:bg-opacity-80 active:text-blue-gray-900",
                    # TODO: make this a component or sth
                    onClick="""event.preventDefault(); 
                           Swal.fire({
                               title: "Zatwierdź usunięcie",
                               icon: "warning",
                               text: "Czy na pewno chcesz usunąć to urządzenie?",
                               showCancelButton: true,
                               cancelButtonText: "Anuluj",
                               confirmButtonText: "Zatwierdź",
                               customClass: {
                                    confirmButton: 'middle none center rounded-md bg-green-500 py-3 px-6 font-sans text-xs font-bold uppercase text-white transition-all active:opacity-[0.85] disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none',
                                    cancelButton: 'px-6 py-3 mr-1 font-sans text-xs font-bold text-red-500 uppercase transition-all rounded-md middle none center hover:bg-red-500/10 active:bg-red-500/30 disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none',
                               },
                           })
                           .then((result) => {
                               if(result.isConfirmed){
                                 htmx.trigger(this, "confirmed");
                               }
                           });
                           """,
                    **{
                        "hx-delete": hx_delete,
                        "hx-trigger": "confirmed",
                    },
                ):
                    Icon("delete")
                    p(
                        delete_text,
                        class_name="block font-sans text-sm antialiased font-medium leading-normal text-inherit",
                    )
                with a(
                    role="menuitem",
                    class_name="flex w-full cursor-pointer select-none items-center gap-2 rounded-md px-3 pt-[9px] "
                    "pb-2 text-start leading-tight outline-none transition-all hover:bg-blue-gray-50 "
                    "hover:bg-opacity-80 hover:text-blue-gray-900 focus:bg-blue-gray-50 "
                    "focus:bg-opacity-80 focus:text-blue-gray-900 active:bg-blue-gray-50 "
                    "active:bg-opacity-80 active:text-blue-gray-900",
                    href=edit_page_url,
                ):
                    Icon("edit")
                    p(
                        edit_text,
                        class_name="block font-sans text-sm antialiased font-medium leading-normal text-inherit",
                    )
